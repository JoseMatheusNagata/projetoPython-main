# 06 — Autenticação e permissões

O app `contas` já está pronto. Este módulo explica **como** ele funciona
— e é o conteúdo mais cobrado na arguição, porque é onde estão as
decisões de segurança.

## Autenticação ≠ autorização

- **Autenticação**: *quem é você?* (login)
- **Autorização**: *o que você pode fazer?* (perfil, permissão)

São perguntas diferentes e têm respostas HTTP diferentes:

| Situação | Resposta | Por quê |
|---|---|---|
| Não está logado | redireciona para o login | não sei quem você é |
| Logado, sem permissão | **403** | sei quem você é, e você não pode |

Mandar para o login alguém que **já está logado** produz aquele loop de
tela de login que não adianta preencher. Por isso o `@somente_coordenacao`
faz 403 no segundo caso.

## O modelo de usuário

```python
class Usuario(AbstractUser):
    class Perfil(models.TextChoices):
        COORDENACAO = "COORD", "Coordenação"
        PROFESSOR = "PROF", "Professor"
        SECRETARIA = "SEC", "Secretaria"

    perfil = models.CharField(max_length=5, choices=Perfil.choices,
                              default=Perfil.SECRETARIA)
```

`AbstractUser` já traz `username`, `password`, `first_name`, `last_name`,
`email`, `is_active`, `is_staff`, `is_superuser`, `last_login` e
`date_joined`. Nós só acrescentamos o `perfil`.

No `settings.py`:

```python
AUTH_USER_MODEL = "contas.Usuario"
```

> **Isso precisa existir antes da primeira migration.** Trocar o modelo
> de usuário com o banco já criado é um dos procedimentos mais dolorosos
> do Django. Por isso o projeto já nasce assim — mesmo raciocínio do
> enunciado da Entrega 1: base torta se paga três vezes.

### `TextChoices`

Um "enum". Ganhos sobre usar a string solta:

- `<select>` pronto no formulário
- `{{ usuario.get_perfil_display }}` mostra "Coordenação", não "COORD"
- no código você escreve `Usuario.Perfil.COORDENACAO` — errou de digitar,
  o Python acusa na hora

## Senhas

```python
Usuario.objects.create_user(username="ana", password="segredo")
```

**Use `create_user`, nunca `objects.create`.** O `create_user` aplica o
*hash*; o `objects.create(password="x")` grava o texto puro e o login
nunca funciona (o Django compara hash com texto).

O que fica no banco é algo como:

```
pbkdf2_sha256$870000$k3Jd...$8Hn2...
```

Um hash é de mão única: dá para conferir se uma senha bate, não dá para
recuperar a senha original. Por isso todo sistema sério manda você
*redefinir* a senha, nunca a envia de volta por e-mail.

Conferir:

```python
usuario.check_password("segredo")   # True ou False
```

Trocar:

```python
usuario.set_password("nova")        # aplica o hash
usuario.save()                      # sem isto, nada é gravado
```

## Sessão: como o Django lembra de você

1. Você envia usuário e senha
2. O Django confere e cria uma **sessão** no banco
3. Devolve um cookie com o **id da sessão** — não com os seus dados
4. A cada requisição, o `AuthenticationMiddleware` lê o cookie, busca a
   sessão e preenche `request.user`

Por isso `request.user` existe em toda view, e `{{ user }}` em todo
template. Para um visitante, `request.user` é um `AnonymousUser` — um
objeto falso cujo `is_authenticated` é sempre `False`.

## Protegendo uma view

```python
from django.contrib.auth.decorators import login_required

@login_required
def aluno_lista(request):
    ...
```

Se não estiver logado, redireciona para `LOGIN_URL`, guardando o destino
em `?next=`. Depois de logar, o usuário volta para onde queria ir.

### O decorator por perfil

```python
def somente_coordenacao(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        if not request.user.eh_coordenacao:
            raise PermissionDenied("Acesso restrito à coordenação.")

        return view(request, *args, **kwargs)

    return wrapper
```

Um **decorator** é uma função que embrulha outra. O `@wraps` preserva o
nome e a docstring da view original — sem ele, toda view passaria a se
chamar `wrapper` e depurar viraria adivinhação.

`PermissionDenied` faz o Django responder 403 e renderizar `403.html`.

## Esconder o link não é proteger

No `base.html`:

```django
{% if user.eh_coordenacao %}
  <a href="{% url 'contas:usuario_lista' %}">Usuários</a>
{% endif %}
```

Isso é **cortesia**, não segurança: não ofereça um botão que vai dar 403.

A proteção de verdade é o decorator na view. Quem digitar a URL
diretamente continua sendo barrado. Esconder sem proteger é o erro
clássico — a URL continua lá.

## CSRF

Todo `<form method="post">` precisa de:

```django
{% csrf_token %}
```

Ele insere um campo escondido com um token único da sessão.

**O ataque que isso impede:** você está logado no sistema acadêmico.
Outro site, aberto em outra aba, tem um formulário escondido que envia um
POST para `/contas/usuarios/3/excluir/`. O seu navegador manda o cookie
de sessão junto, automaticamente — e o sistema obedeceria, achando que
foi você. O token quebra isso, porque o site malicioso não tem como
descobri-lo.

Esqueceu o `{% csrf_token %}`? O sintoma é 403 ao enviar o formulário. É
o erro número 1 de quem está começando.

### Logout por POST

Desde o Django 5, logout exige POST — por isso o botão "Sair" é um
formulário, não um link. Se fosse GET, um site malicioso deslogaria você
só por embutir `<img src="http://.../logout/">`.

## Soft delete

A gestão de usuários não apaga ninguém: marca `is_active = False`.

```python
usuario.is_active = False
usuario.save(update_fields=["is_active"])
```

Por que:

- **Histórico.** Quem lançou notas no semestre passado não pode sumir; as
  notas ficariam órfãs e o registro, sem autor.
- **Reversível.** Desativar por engano se conserta com um clique. `DELETE`
  não.
- **Auditoria.** Numa instituição de ensino, é frequente precisar saber
  quem fez o quê, anos depois.

O Django já respeita `is_active`: usuário inativo não consegue logar,
mesmo com a senha certa. Não é só uma flag decorativa.

O `update_fields=["is_active"]` faz o `UPDATE` gravar só aquela coluna,
em vez de reescrever a linha inteira.

> Essa decisão vale ponto no bônus do trabalho — e a pergunta é sua para
> responder: num sistema acadêmico, o que se ganha e o que se perde ao
> nunca apagar de verdade?

## A trava que parece paranoia

```python
if usuario == request.user and not form.cleaned_data["is_active"]:
    messages.error(request, "Você não pode desativar a sua própria conta.")
```

Sem isso, a coordenação se tranca fora do sistema e não há como voltar
pela interface — só pelo shell do Django.

Esse tipo de trava é o que separa um CRUD de um sistema.

---

Anterior: [05 — Views, URLs e templates](05-views-urls-templates.md) ·
Próximo: [07 — Tour do app `contas`](07-tour-do-app-contas.md)
