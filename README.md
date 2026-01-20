# checador-de-inventario3k

  Feito com muito ódio por DrLegato com notepad++ porque o TI (Arcontes do Demiurgo) não me deixa usar o VStudio sem ter que passar por 15 anos de burocracia
 
  
  nem FUDENDO que eu vou checar 69 páginas de código de exemplar pra ver se ter duplicatas
  
 então eu fiz essa merda inteira em uma hora e meia com auxílio de 2 latas de redbull e 1 camel amarelo
 
 
 não houve qualquer tipo de teste depois de feito e eu ver que funciona na minha máquina
 
 pode ser que ele reverta a entropia local de onde você rodar 
 

 esse programa foi feito pra uso pessoal, não garanto NEM O MÍNIMO ESPERADO

 só tá no github por fins de arquivo.

enfim: 

checadordeinventario3k.py

O que essa porra faz?
Escaneia arquivo indicado procurando:
- linhas duplicadas (string exata duas vezes)
- IDs disformes (baseado em regras que tu definir)
- quase-duplicados (mesmos digitos apos normalização)

o que precisa pra rodar esta desgraça?
- python
- algo um pouco mais potente que o ENIAC
- a habilidade de ler
- um arquivo pra checar (se for .docx, leia abaixo o que fazer)

Essa merda suporta:
- .txt / .csv / .tsv / plain text no geral
- .docx (via python-docx)
- o resto tá na mão de Deus, Odin, Rah, Sophia, Shiva, que seja.

Como usar essa caralha:
- python checadordeinventario3k.py path/to/file.docx
- python checadordeinventario3k.py path/to/file.txt --comprimento_esperado 9 (comprimento que tu quiser)
- python checadordeinventario3k.py path/to/file.txt --csv-out report_prefix

Dependencia pra .docx:
  pip install python-docx
  
  
  
 F.A.Q:
 
 - 'ain mas seu codigo ta muito sujo'
  - ta funcionando entao nao mexe
  - 'ain mas pra que usar python? usa [insira linguagem aqui]'
  - parceiro, eu sou um bibliotecário que tem dois certificados de programação, um é com python e o outro é ruby. se tu quer tanto mudar a linguagem usada, fique à vontade.
  
  - forte abraço, tomara que nada exploda
- 'hotel?'
- trivago.

  escrever isso tudo foi muito terapêutico.
  boa noite, boa sorte,

  
  DrLegato
  
