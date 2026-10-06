# 07 — Tour guiado do app `contas`

O app `contas` é a implementação de referência: cada arquivo dele é a
resposta de uma pergunta que você vai ter ao escrever o app `academico`.

**Leia este módulo com os arquivos abertos ao lado.** É o módulo mais
útil do material.

## O mapa

| Arquivo em `contas/` | Responde | Equivalente em `academico/` |
|---|---|---|
| `models.py` | como declaro uma tabela? | TODO 1, 2 e 3 |
| `forms.py` | como coleto e valido? | TODO 4, 5 e 6 |
| `views.py` | como faço o CRUD? | TODO 7 a 12 |
| `urls.py` | como ligo URL à view? | já vem pronto |
| `admin.py` | como inspeciono os dados? | TODO 13 (bônus) |
| `decorators.py` | como restrinjo acesso? | reaproveite |
| `tests.py` | como testo? | leia antes de rodar `verificar.py` |

## `models.py` — o modelo `Usuario`

Repare em quatro coisas:

**1. A herança.** `class Usuario(AbstractUser)` — herdamos tudo que o
Django precisa para autenticar e só acrescentamos `perfil`.

**2. O `TextChoices`.** Um enum, aninhado dentro da classe. Isso dá
`<select>` pronto, rótulo legível e checagem em tempo de código.

**3. O `Meta`.** `db_table = "usuario"` fixa o nome da tabela;
`ordering` define a ordem padrão de toda consulta.

**4. A regra de negócio no modelo:**

```python
@property
def eh_coordenacao(self):
    return self.is_superuser or self.perfil == self.Perfil.COORDENACAO
```

A pergunta "esta pessoa é da coordenação?" tem **uma** resposta, num
lugar só — e ela funciona igual na view, no template (`{% if
user.eh_coordenacao %}`) e no teste.

> **Pergunta de arguição:** por que o superusuário também passa nessa
> checagem?
> Porque quem instala o sistema precisa conseguir entrar na gestão
> *antes* de existir qualquer usuário de coordenação — é o caso do
> `admin` criado pelo `seed_demo`.
> Sem isso, o sistema nasce inacessível.

## `forms.py` — três formulários, três motivos

**`LoginForm`** herda de `AuthenticationForm`, que o Django já traz
pronto. Nós só ajustamos aparência e textos.

> Por que não escrever o login na mão? Porque o Django já resolve
> comparação de hash, conta inativa e redirect seguro melhor do que
> qualquer um de nós faria. **Escrever código é custo, não virtude.** Se
> o framework já resolveu, use. Isso é RAD.

**`UsuarioCriarForm`** herda de `UserCreationForm`: traz os dois campos
de senha, confere se batem, aplica os validadores e grava com hash.

**`UsuarioEditarForm`** é separado — e a razão é boa: editar **não** deve
pedir senha. Se os campos de senha estivessem aqui, quem quisesse
corrigir um sobrenome teria que redigitar a senha.

### O detalhe que vale ouro

Compare os dois `clean_email`:

```python
# Criar
Usuario.objects.filter(email=email).exists()

# Editar
Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists()
```

Ao **editar**, o próprio usuário já está no banco com aquele e-mail. Sem
o `.exclude()`, a busca acha ele mesmo e acusa duplicidade sempre —
editar qualquer usuário ficaria impossível.

Em SQL: `WHERE email = %s AND id <> %s`.

Esse padrão vale para qualquer campo único que você valide na mão.

## `views.py` — o CRUD, lado a lado com a Entrega 1

| View | Faz | Na Entrega 1 era |
|---|---|---|
| `usuario_lista` | `.all()` + busca com `Q` | `listar_alunos()` |
| `usuario_detalhe` | `get_object_or_404` | `buscar_aluno_por_id()` |
| `usuario_novo` | POST/Redirect/GET | `inserir_aluno()` |
| `usuario_editar` | idem, com `instance=` | `atualizar_aluno()` |
| `usuario_excluir` | GET confirma, POST executa | `excluir_aluno()` |

Quatro coisas para observar enquanto lê:

**1. O `if request.method == "POST"`.** Sempre o mesmo desenho. Se você
entender esse bloco, entendeu seis dos doze TODOs.

**2. O `redirect` depois do `save()`.** POST/Redirect/GET. Sem ele, F5
duplica o registro.

**3. O `instance=usuario` no editar.** É a única diferença entre criar e
editar. Aparece nos dois caminhos, no GET e no POST.

**4. A variável de contexto se chama `usuario_obj`, não `usuario`.**

Isso é deliberado: o context processor `auth` já injeta `{{ user }}` em
todo template. Se a view mandasse a variável como `user`, ela
sobrescreveria aquela — e a navbar passaria a mostrar o usuário sendo
*visitado* como se fosse você. Bug sutil, difícil de achar, e
perfeitamente evitável escolhendo outro nome.

### A trava de auto-desativação

```python
if usuario == request.user:
    messages.error(request, "Você não pode desativar a sua própria conta.")
    return redirect("contas:usuario_lista")
```

Repare que ela aparece **duas vezes**: no `usuario_editar` e no
`usuario_excluir`. São dois caminhos diferentes para o mesmo estrago, e
fechar só um deixa a porta aberta.

## `decorators.py` — 20 linhas que valem a leitura

É o arquivo mais curto e um dos mais importantes. Ele mostra que
`@login_required` não é mágica: é uma função que embrulha outra e decide
se ela deve rodar.

**Reaproveite este decorator no app `academico`** se quiser restringir
alguma tela por perfil — por exemplo, deixar o lançamento de notas só
para professores. Vale bônus, e é uma linha:

```python
from contas.decorators import somente_coordenacao
```

## `tests.py` — leia antes de reclamar do `verificar.py`

21 testes cobrindo login, permissão e CRUD. Eles são o gabarito de como
se escreve teste em Django, e valem por três razões:

- provam que o app funciona sem ninguém clicar na tela;
- travam regressão: se alguém quebrar o soft delete, o teste avisa;
- documentam o comportamento esperado melhor que qualquer comentário.

Rode:

```bash
python manage.py test contas -v 2
```

Repare em `test_get_na_exclusao_nao_desativa`: ele garante que abrir a
URL de exclusão **não** desativa ninguém. É pequeno, e é o que separa um
sistema de uma bomba-relógio.

## As perguntas da arguição

Se você consegue responder estas dez, está pronto:

1. Por que `Usuario` herda de `AbstractUser` em vez de usar o `User`
   padrão?
2. Onde a senha é transformada em hash, e por que não dá para
   recuperá-la?
3. O que acontece entre clicar em "Entrar" e ver a lista de usuários?
4. Por que existe `UsuarioCriarForm` **e** `UsuarioEditarForm`?
5. O que o `.exclude(pk=self.instance.pk)` do `clean_email` evita?
6. Qual é a única diferença entre a view de criar e a de editar?
7. Por que a exclusão só acontece no POST?
8. Por que a variável do template se chama `usuario_obj` e não `usuario`?
9. Esconder o link da gestão no `base.html` protege a tela? Por quê?
10. O que o `{% csrf_token %}` impede, concretamente?

---

Anterior: [06 — Autenticação e permissões](06-autenticacao-e-permissoes.md) ·
Próximo: [08 — Roteiro do trabalho](08-roteiro-do-trabalho.md)
