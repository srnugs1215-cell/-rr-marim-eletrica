# RR Marim Elétrica — aplicativo Android offline

Este projeto gera um APK Android com interface de celular e o motor de cálculo Python incorporado. Depois de instalado, o aplicativo não precisa de internet para calcular.

## O que está incluído
- Cadastro de projeto, sistema de tensão e tipo de fornecimento.
- Cadastro de cômodos e cargas específicas (TUE).
- Cálculo usando o motor original `dimensionador.py`.
- Geração de relatório PDF e gravação de projetos em JSON no armazenamento privado do app.

## Como gerar o APK sem instalar ferramentas no computador
1. Crie uma conta no GitHub, se ainda não tiver.
2. Crie um repositório novo e envie **todos os arquivos e pastas deste pacote** para a raiz do repositório, incluindo a pasta `.github`.
3. Abra a aba **Actions** do repositório e habilite os workflows, se o GitHub pedir.
4. Aguarde a execução **Build Android APK** terminar com sucesso.
5. Abra a execução concluída, desça até **Artifacts** e baixe `RR-Marim-Eletrica-APK`.
6. Extraia o ZIP baixado e instale o APK no Android. O Android pode pedir autorização para instalar apps dessa fonte.

Também pode iniciar a compilação manualmente em Actions → Build Android APK → Run workflow.

## Observações importantes
- O APK ainda precisa ser compilado pelo workflow; este pacote contém o código-fonte, não um APK já compilado.
- A primeira compilação pode demorar vários minutos.
- O relatório PDF e os projetos ficam no armazenamento privado do aplicativo. A interface de exportação/compartilhamento para a pasta Downloads pode ser adicionada numa próxima versão.
- Antes de usar em obra, um profissional habilitado deve conferir o motor de cálculo, os critérios adotados, a edição aplicável da ABNT NBR 5410 e as condições reais da instalação. O aplicativo é ferramenta auxiliar, não substitui projeto e verificação técnica.
