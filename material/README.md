# Material de estudo — Sistema de Registro Acadêmico

Este material existe para atravessar um vão específico: você aprendeu a
falar com o banco escrevendo SQL na mão, com `sqlite3`, e agora vai fazer
a mesma coisa através de um framework que escreve o SQL por você.

Nada do que você aprendeu na Entrega 1 foi jogado fora. O que muda é a
**camada** onde você trabalha — e cada módulo daqui mostra a tradução.

## Ordem de leitura

| # | Módulo | Leia antes de |
|---|---|---|
| [00](00-instalacao.md) | Instalação e primeiro run | qualquer coisa |
| [01](01-de-sqlite-cru-para-django.md) | De `sqlite3` cru para Django | começar a estudar o projeto |
| [02](02-models-e-migrations.md) | Models e migrations | TODO 1, 2 e 3 |
| [03](03-orm-na-pratica.md) | ORM na prática | TODO 7 e 12 (e a Entrega 2) |
| [04](04-forms-e-validacao.md) | Forms e validação | TODO 4, 5 e 6 |
| [05](05-views-urls-templates.md) | Views, URLs e templates | TODO 7 a 12 |
| [06](06-autenticacao-e-permissoes.md) | Autenticação e permissões | mexer em acesso |
| [07](07-tour-do-app-contas.md) | Tour guiado do app `contas` | escrever a sua primeira view |
| [08](08-roteiro-do-trabalho.md) | Roteiro do trabalho | organizar o grupo |
| [09](09-erros-comuns.md) | Erros comuns | quando travar |
| [10](10-glossario-e-cbv.md) | Glossário e Class-Based Views | revisar / buscar bônus |

## O caminho mais curto

Com pressa? Leia **00**, **01** e **07**, nessa ordem, e comece o
**08**. Os outros módulos você consulta conforme os TODOs pedirem.

## Uma observação sobre o app `contas`

O app de contas (login e gestão de usuários) **já está pronto**. Ele não
é um enfeite: é a resposta, escrita e comentada, de toda pergunta que
você vai ter ao implementar o app `academico`.

Sempre que travar, abra o arquivo equivalente em `contas/` e compare.
