<div align="center">

# 🏨 Onfly — Consolidador de reservas de hotel

### Relatório de entrega

![Python](https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-_%2F_%20passed-brightgreen?logo=pytest&logoColor=white)

**Candidato(a):** _Leonardo Romano Andrade_ · **Data:** _2026-11-14_  

</div>

## 🎯 Resumo

A ideia central desse projeto é fazer um sistema que calcula preços de hotéis com base em uma demanda enviada como entrada. Porém, o código apresentava uma gama de erros que impedia o cálculo correto desses preços e não fornecia informações fidedignas (ou coerentes) do que deveria ser informado.

| | Antes | Depois |
|-|:-:|:-:|
| Testes fornecidos (`pytest tests`) | 0 / 5 ❌ | 5 / 5 ✅ |
| `total_reservations` (base real) | 200 | 300 |
| `total_room_nights` (base real) | **-1393** | 1347 |
| `total_amount_brl` (base real) | 193218.53 | 396170.00 |
| `average_nightly_rate_brl` (base real) | 0.00 | 294.11 |
| Divergências contra o gabarito (5 bases) | 185 | 0 |

Aqui, podemos ver várias inconsistências de cálculos no nosso sistema: <br><br>
I)   O programa considera, apenas, 200 das 300 reservas do arquivo de entrada <br>
II)  O cálculo da quantidade de noites está negativo (o que não faz sentido) <br>
III) O valor monetário está muito diferente do esperado <br>

---

## ♟️ Estratégia utilizada

Para corrigir o problema, criei um novo script que calculava todos os valores (quantidade de noites, número de reservas, valor monetário, etc), seguindo os requisitos das regras de negócio.<br>
Depois disso, fiz um comparativo entre cada cálculo do meu novo script contra os valores encontrados pelo CLI. Com isso, eu conseguia encontrar, exatamente, onde o sistema errava e quais valores eram inconsistentes. <br> <br>
Além disso, gerei um arquivo de testes diferente do original, colocando casos de borda (com cálculos de arredondamentos diferentes, empates no ranqueamento e maior número de linhas no .csv), com cenários não cobertos pelos testes fornecidos. <br><br>
Veja o exemplo que mostra a comparação dos erros abaixo. <br>

#### Exemplo: comparativo na amostra de validação, com o código original

```bash
python my_tests/comparar.py --input data/exemplo-validacao.csv --so-erros
```

```text

====================================================================================================
Base: data/exemplo-validacao.csv  (--top 5)
====================================================================================================
  campo                                      esperado      obtido (CLI)  resultado
  summary.total_room_nights                        28               -33  ERRO <<<
  summary.total_amount_brl                    7566.00           5962.41  ERRO <<<
  summary.average_nightly_rate_brl             270.21              0.00  ERRO <<<
  by_month[2025-01].reservations                    8                 9  ERRO <<<
  by_month[2025-01].room_nights                    25               -36  ERRO <<<
  by_month[2025-01].total_brl                 6684.00           5936.90  ERRO <<<
  by_month[2025-02].total_brl                  882.00             25.51  ERRO <<<
  top_hotels[0].hotel_id                          H01               H09  ERRO <<<
  top_hotels[0].hotel_name           Hotel Aurora Paulista  Hotel Lisboa, Centro  ERRO <<<
  top_hotels[0].total_brl                     1200.00             25.51  ERRO <<<
  top_hotels[1].total_brl                     1084.00             36.90  ERRO <<<
  top_hotels[2].hotel_id                          H12               H05  ERRO <<<
  top_hotels[2].hotel_name           Hotel Miami Beach  Hotel Recife Plaza  ERRO <<<
  top_hotels[2].total_brl                     1000.00            300.00  ERRO <<<
  top_hotels[3].hotel_id                          H10               H08  ERRO <<<
  top_hotels[3].hotel_name           Hotel Madrid, Gran Vía  Hotel Iguazu Falls  ERRO <<<
  top_hotels[3].room_nights                         4                 1  ERRO <<<
  top_hotels[3].total_brl                      900.00            400.00  ERRO <<<
  top_hotels[4].hotel_id                          H09               H07  ERRO <<<
  top_hotels[4].hotel_name           Hotel Lisboa, Centro  Hotel Brasília Tower  ERRO <<<
  top_hotels[4].room_nights                         3                 2  ERRO <<<
  top_hotels[4].total_brl                      882.00            600.00  ERRO <<<
  => 22/44 campos corretos, 22 divergente(s)

RESULTADO GERAL: 22 divergência(s)
```

Usando essa execução como referência, podemos, modificar trechos do código original do CLI e verificar se a quantidade de erros diminui com as alterações, além de cobrir outros cenários com o novo arquivo utilizado.

## 🐞 Defeitos corrigidos

### 1: Quantidade de noites

O primeiro problema tratado foi a quantidade inconsistente de noites, que apresentava um valor negativo. <br>
Curiosamente, a solução para esse erro se encontrava, justamente, na especificação do problema (README.md do arquivo original). <br><br>
Na linha 67 da especificação, temos o seguinte trecho: 
```
room\_nights = (checkout\_date - checkin\_date).days \* rooms
```
<br>
Que gera um comportamento correto, uma vez que calcula a quantidade de dias entre as duas datas e depois multiplica pelo número de quartos.<br> 
Porém, no código original (services\stay_calculator.py - linha 10), temos o seguinte trecho:

```
return (checkout.day - checkin.day) * rooms
```

<br> 
Esse retorno tem um problema enorme, pois calcula o dia antes de calcular a diferença das datas. Se tivermos uma data de checkin como 30/10/2026 e uma data de checkout como 01/11/2026, o retorno faz o seguinte cálculo:<br><br>
(1 - 30) * rooms => (-29) * rooms 
<br> <br>
Gerando um valor negativo para a quantidade de noites. <br><br>

#### Correção:

Para fazer com que o script funcionasse corretamente, troquei o retorno original: <br> 

```diff
- return (checkout.day - checkin.day) * rooms
+ return (checkout - checkin).days * rooms
```

E os resultados da quantidade de noites ficou mais coerente. <br>
Por enquanto, o número de noites ainda não estava coerente, pois o programa ainda não lia todo o arquivo. Ao atacar o problema do processamento de leitura, veremos que essa mudança, de fato, corrige o problema do cálculo de noites.

---

### 2: Valor monetário

O segundo problema tratado foi o valor monetário, que aparecia muito abaixo do esperado sempre que a reserva estava em uma moeda estrangeira. <br>
Mais uma vez, a especificação do problema já dizia como o cálculo deveria ser feito. <br><br>
Na linha 76 da especificação, temos o seguinte trecho:
```
Converta com amount * rate_to_brl, usando a tabela data/taxas_cambio.csv.
```
<br>
E, nas linhas 93 e 94, temos:

```
Use Decimal, nunca float, no dinheiro.
Some os valores exatos e arredonde só na serialização, para 2 casas, com half-up.
```
<br>
Porém, no código original (services\currency_converter.py - linha 11), temos o seguinte trecho:

```
return Decimal(str(float(amount) / float(rate)))
```

<br>
Esse retorno tem dois problemas. O primeiro é que ele <b>divide</b> o valor pela taxa, quando deveria multiplicar. Se tivermos uma reserva de USD 100,00 com a taxa de 5,42, o retorno faz o seguinte cálculo:<br><br>
100,00 / 5,42 => 18,45 (o correto seria 100,00 * 5,42 => 542,00)
<br><br>
As reservas em BRL saíam certas por acaso, já que a taxa do real é 1 e tanto faz dividir ou multiplicar. Por isso, o erro só aparecia nas reservas em USD e EUR. <br><br>
O segundo problema é o uso do <code>float</code>, que perde precisão nas casas decimais. Mesmo que a divisão fosse trocada por uma multiplicação, uma reserva de USD 0,75 faria o seguinte cálculo:<br><br>
0,75 * 5,42 => 4,0649999999999995 => 4,06 (o correto seria 4,065 => 4,07)
<br><br>
Gerando um centavo de diferença, que vai se acumulando quando os valores são somados. <br><br>

#### Correção:

Para fazer com que o script funcionasse corretamente, troquei o retorno original: <br>

```diff
- return Decimal(str(float(amount) / float(rate)))
+ return amount * rate
```

Como o <code>amount</code> e o <code>rate</code> já chegam ao conversor como <code>Decimal</code>, a multiplicação é exata e mantém todas as casas decimais até o final. O arredondamento continua acontecendo uma única vez, no momento de gerar o JSON (<code>format_money</code>, em services\report_builder.py). <br>
Para garantir que isso estava correto, criei uma base só com casos de arredondamento (ex.: 3 * 4,065 = 12,195 => 12,20, enquanto arredondar cada reserva antes daria 12,21). Com essa mudança, os valores ficaram corretos, mas o ranking de hotéis continuava estranho, mesmo com todos os valores batendo.

---

### 3: Ranking de hotéis

O terceiro problema tratado foi o ranking de hotéis (<code>top_hotels</code>), que mostrava os hotéis errados. <br>
Depois de corrigir as noites e o valor monetário, percebi que, na minha base de arredondamento, todos os valores estavam corretos e, mesmo assim, o ranking aparecia ao contrário. <br><br>
Na linha 102 da especificação, temos o seguinte trecho:
```
top_hotels: total_brl decrescente; empate por hotel_id ascendente.
```
<br>
Porém, no código original (services\report_builder.py - linha 91), temos o seguinte trecho:

```
ranked_hotels = sorted(hotels.items(), key=lambda item: (item[1]["amount"], item[0]))
```

<br>
Esse trecho tem um problema, pois o <code>sorted()</code> ordena de forma crescente por padrão. Logo depois, o código pega os primeiros itens da lista (<code>[: self._top_n]</code>), ou seja, os hotéis com o <b>menor</b> faturamento. Se tivermos três hotéis com R$ 100,00, R$ 200,00 e R$ 300,00, o ranking fica da seguinte forma:<br><br>
H01 (100,00) => H02 (200,00) => H03 (300,00)
<br><br>
Quando o correto seria H03 => H02 => H01. <br><br>

#### Correção:

Para fazer com que o script funcionasse corretamente, troquei o trecho original: <br>

```diff
- ranked_hotels = sorted(hotels.items(), key=lambda item: (item[1]["amount"], item[0]))
+ ranked_hotels = sorted(hotels.items(), key=lambda item: (-item[1]["amount"], item[0]))
```

Negar o valor faz com que ele seja ordenado de forma decrescente, sem mexer no desempate pelo <code>hotel_id</code>, que continua crescente. <br>
Antes disso, testei a solução com <code>reverse=True</code>. Ela fazia o teste fornecido passar, mas invertia também o desempate (H09, H05, H02 em vez de H02, H05, H09). Por isso, descartei essa alternativa e criei testes específicos para o caso de empate. Com essa mudança, o ranking da amostra ficou idêntico ao da especificação, mas o número de reservas ainda não batia.

---

### 4: Reservas NO_SHOW

O quarto problema tratado foi a contagem de reservas, noites e valores, que ainda aparecia um pouco acima do esperado. <br>
Na amostra de validação, o programa mostrava 29 noites em vez de 28 e 9 reservas em janeiro em vez de 8. <br><br>
Nas linhas 60 e 61 da especificação, temos o seguinte trecho:
```
Só CONFIRMED é faturável.
CANCELLED e NO_SHOW contam em total_reservations e nas contagens por status, mas não entram em noites, valores, by_month nem top_hotels.
```
<br>
Porém, no código original (services\status_policy.py - linha 8), temos o seguinte trecho:

```
return status != "CANCELLED"
```

<br>
Esse retorno tem um problema, pois considera faturável qualquer reserva que não seja CANCELLED. Ou seja, as reservas NO_SHOW também entravam nos cálculos. Na amostra de validação, a reserva EX-05 é NO_SHOW e tem 1 noite, então o cálculo ficava da seguinte forma:<br><br>
28 noites (CONFIRMED) + 1 noite (NO_SHOW) => 29 noites
<br><br>
Fiz essa conta, reserva por reserva, em todas as bases, e a diferença de noites era sempre exatamente a soma das noites das reservas NO_SHOW. <br><br>

#### Correção:

Para fazer com que o script funcionasse corretamente, troquei o retorno original: <br>

```diff
- return status != "CANCELLED"
+ return status == "CONFIRMED"
```

Assim, em vez de dizer o que não é faturável, o código passa a dizer exatamente o que é faturável. Se aparecer algum status novo ou inesperado, ele nunca vai entrar nos totais por acidente. <br>
Com essa mudança, os 5 testes fornecidos passaram. Porém, a base real ainda mostrava apenas 200 reservas, enquanto o arquivo tem 300.

---

### 5: Leitura do arquivo

O quinto e último problema tratado foi a leitura do arquivo de entrada, que considerava apenas 200 das 300 reservas da base real. <br>
Esse era o erro mais escondido, pois nenhum dos testes fornecidos usa mais de 200 reservas. Ou seja, mesmo com todos os testes passando, o relatório da base real continuava errado. Só encontrei o problema porque rodei o meu comparativo na base real e em uma base forjada com 260 linhas. <br><br>
Na linha 81 da especificação, temos o seguinte trecho:
```
total_reservations = número de reservas no arquivo.
```
<br>
Porém, no código original (repositories\csv_reservation_repository.py - linhas 47 e 48), temos o seguinte trecho:

```
if len(rows) == 200:
    break
```

<br>
Esse trecho tem um problema enorme, pois interrompe a leitura do arquivo ao chegar na 200ª reserva e descarta todo o resto, sem nenhum aviso ou erro. Na base real, o programa fazia o seguinte:<br><br>
300 reservas no arquivo => 200 reservas lidas => 100 reservas ignoradas
<br><br>
Com isso, todas as informações do relatório ficavam menores do que deveriam: as contagens por status, as noites, os valores e o ranking. Além disso, a própria documentação dessa classe diz que ela "lê a exportação de reservas sem aplicar regra de negócio", e esse limite de 200 é justamente uma regra escondida. <br><br>

#### Correção:

Para fazer com que o script funcionasse corretamente, removi o trecho original: <br>

```diff
  for values in reader:
      rows.append(RawRow(line_number=reader.line_num, values=values))
-     if len(rows) == 200:
-         break
  return rows
```

E o laço de leitura passou a percorrer o arquivo inteiro. <br>
Com essa mudança, o número de noites finalmente ficou correto (1347 noites na base real), confirmando que a correção do primeiro problema estava certa. O comparativo entre o meu script e o CLI zerou as divergências nas 5 bases, e criei testes com mais de 200 reservas para que esse erro não volte a acontecer sem ser percebido.


## 🛡️ Robustez

Depois de corrigir os 5 defeitos, criei novos testes na pasta `tests/` para garantir que esses erros não voltem a acontecer e para cobrir casos que os testes fornecidos não verificavam. <br>
Todos seguem o mesmo formato dos testes originais e estão nomeados como `test_my_*`, sem alterar nenhum dos testes fornecidos. <br><br>

**`test_my_nights.py` (5 testes)** <br>
Verifica o cálculo de noites na virada de ano, em ano bissexto (28/02 a 01/03/2024) e com mais de um quarto. Também garante que uma estadia que cruza o mês entra inteira no mês do check-in.

**`test_my_currency.py` (6 testes)** <br>
Verifica que o valor é sempre multiplicado pela taxa (BRL, USD e EUR) e que as casas decimais são mantidas até o final (333,33 EUR => 1959,9804 => 1959,98).

**`test_my_rounding.py` (13 testes)** <br>
Verifica o arredondamento half-up com casos em que a terceira casa decide o resultado (4,065 => 4,07). Também garante que o arredondamento acontece só depois da soma (3 * 4,065 => 12,20, e não 12,21) e que a média por noite usa o valor exato.

**`test_my_status_rules.py` (4 testes)** <br>
Verifica que reservas NO_SHOW e CANCELLED não entram em `by_month` nem em `top_hotels`, que uma base sem reservas CONFIRMED tem média `0.00` e que a soma das contagens por status bate com o total.

**`test_my_top_hotels.py` (6 testes)** <br>
Verifica o desempate por `hotel_id` (inclusive no corte do `--top`), o `--top 1`, um `--top` maior que o número de hotéis e nomes com vírgula e acento. São esses testes que pegam o erro da alternativa com `reverse=True`.

**`test_my_large_file.py` (2 testes)** <br>
Verifica que arquivos com mais de 200 reservas são lidos por inteiro, inclusive um hotel que só aparece depois da linha 200. São os testes que cobrem o quinto defeito.

**`test_my_regression_data.py` (3 testes)** <br>
Roda o CLI nos arquivos de `data/` e compara o relatório inteiro com os valores esperados: a amostra de validação com a tabela da especificação, e a base real com 300 reservas, 1347 noites e R$ 396.170,00.

**`test_my_report_format.py` (8 testes)** <br>
Verifica o formato do relatório: nomes e ordem das chaves, tipos dos campos, dinheiro sempre com 2 casas, `generated_at` com offset `-03:00`, o resumo impresso no terminal e o caminho padrão de saída.

**`test_my_cli_errors.py` (39 testes)** <br>
Verifica que entradas e argumentos inválidos terminam com o código de saída `2` e sem gerar relatório: `--top` inválido, arquivos inexistentes, cabeçalho errado, datas fora do formato `YYYY-MM-DD`, valores e quartos inválidos e tabela de câmbio com taxa negativa ou vazia.

---

## ✅ Como validar

```bash
PYTHONPATH=src python -m onfly_report \
  --input data/reservas_hoteis.csv \
  --rates data/taxas_cambio.csv \
  --output output/report.json

pytest -q
```

Saída do CLI na base real:
```text
Reservas: 300 | Confirmadas: 235 | Noites: 1347 | Total BRL: 396170.00
```

Resultado do `pytest`:
```text
........................................................................
...................                                                      [100%]
91 passed in 2.64s
```

Os 5 testes fornecidos passam sem nenhuma alteração, junto com os 86 testes novos.

---

## 🏁 Conclusão

O CLI apresentava 5 defeitos que, juntos, faziam o relatório entregar números errados: <br><br>
I)   As noites eram calculadas pelo dia do mês, gerando valores negativos <br>
II)  O câmbio dividia o valor pela taxa e usava `float` <br>
III) O ranking de hotéis mostrava os piores hotéis em vez dos melhores <br>
IV)  As reservas NO_SHOW entravam nos totais <br>
V)   O programa lia apenas as 200 primeiras reservas do arquivo <br><br>

Todas as correções foram pequenas (uma ou duas linhas cada) e, na maioria dos casos, a resposta estava na própria especificação do problema. O mais importante foi conseguir encontrar exatamente onde cada erro estava, e o comparativo entre o meu script e o CLI foi o que tornou isso possível. <br>
Hoje, o relatório da base real bate com o esperado em todos os campos, os 5 testes fornecidos passam e os novos testes garantem que esses erros não voltem a acontecer, incluindo o quinto defeito, que nenhum teste original conseguia detectar. <br><br>

O uso de IA nesse projeto está registrado em [`uso-de-ia/`](uso-de-ia/).

<div align="center">
<sub>Feito para o processo seletivo da Onfly</sub>
</div>
