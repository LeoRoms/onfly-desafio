Declaração - uso de IA 
Leonardo Romano Andrade
14 / 11 / 2026

---

Para este Projeto, utilizei o modelo do Claude: OPUS 5.5

O modelo me ajudou no desenvolvimento inicial, escrevendo um modelo correto que calculava, corretamente, os valores esperados pelo CLI. <br><br>
Eu ajustei o script feito por ele para agregar, também, os valores de saída do CLI e comparar os resultados corretos com os resultados do sistema.<br><br>
Com essa ajuda, foi mais fácil identificar onde os erros ocorriam e quais os ajustes a serem feitos. Eu encontrei, por conta própria, os locais onde deveriam ser feitos os ajustes. <br><br>
Depois de ajustar os valores, pedi ao claude para gerar um arquivo de testes mais robusto, com mais valores e problemas que poderiam não estar inclusos nos arquivos fornecidos. Eu utilizei eles como base para corrigir o resto dos problemas. <br><br>
Percebi que os novos arquivos fornecidos por ele não geravam nenhum novo problema e a comparação de testes identificava que não havia diferenças entre o CLI e o modelo criado pelo claude. <br><br>
Depois, pedi ao claude para criar novos testes (identificados como 'test_my_*') que seguiam o modelo dos testes fornecidos para tentar abonar mais falhas que o sistema poderia falhar. Felizmente, todos os testes passaram e tudo rodou normalmente. <br><br>
Finalmente, pedi ao claude para gerar um template para o relatótio de entrega 'README-ENTREGA.md' que serviu como uma ajuda inicial para escrever o relatório, porém foi amplamente modificado para que ficasse de acordo com a minha visão de relatório.