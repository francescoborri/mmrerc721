# `MmrERC721`

## Generazione di MMR *proof* consecutivi per `mint`

Il seguente comando genera $n$ input per `mint`, ossia $2n$ MMR *proof* per elementi consecutivi e un indirizzo Ethereum, e li scrive nel file `out_file_path`.

```bash
$ cargo run --bin gen_mint_inputs -- <out_file_path> <n> <to_address>
```

Alla riga $1\leq i \leq n$ saranno presenti il MMR proof per l'elemento $i-1$ (`prevTokenProof`) e l'elemento $i$ (`nextTokenProof`).

La prima `mint` non verifica `prevTokenProof`, in quanto non c'è ancora alcun *token*, per cui il *proof* per l'elemento $0$ ha valori arbitrari che non verranno verificati da `mint`.

L'esecuzione di `mint` con i parametri alla riga $i$ genera un *token* con valore $i$.

In cima a ogni riga viene inoltre aggiunto il valore di `<to_address>`, ossia l'indirizzo a cui inviare i *token* generati, così da far combaciare ogni riga con i parametri di `mint`. `<to_address>` è una stringa esadecimale che inizia con `0x` e rappresenta un indirizzo Ethereum.

## Generazione di MMR *proof* per `verify`

Il seguente comando genera $n$ input per `verify`, ossia $n$ MMR *proof*, e li scrive nel file `out_file_path`.

```bash
$ cargo run --bin gen_verify_inputs -- <out_file_path> <n>
```

La riga $1\leq i \leq n$ del file `out_file_path` conterrà il MMR proof per il primo elemento di un MMR composto da $i$ elementi. Il MMR proof è relativo al primo elemento poiché è quello più costoso da verificare in un MMR con $i$ elementi.

## Generazione dei grafici

Una volta ottenuti i file riguardanti il consumo di gas di `mint` e `verify`, tramite i comandi sopra descritti, è possibile generare i grafici che mostrano l'andamento del costo in gas al crescere della dimensione della collezione di *token*. I file necessari sono `data/gas/mint.csv`, che deve contenere il costo in gas di `mint`, `data/gas/verify.csv`, che deve contenere il costo in gas di `verify`, e `data/gas/max_verify.csv`, che deve contenere il costo in gas di `verify` per diversi valori di $2^i-1$, $2^i$ e $2^i+1$, così da poter visualizzare il costo massimale di `verify` alle diverse altezze del MMR.

Nella cartella `data/collections/transfers` possono essere inoltre inseriti file contenenti informazioni su trasferimenti di *token*, in modo tale da poter simualare il costo di `mint` e `verify` in collezioni di *token* reali.

Nella cartella `scripts` sono presenti gli script per generare i file intermedi necessari alla generazione dei grafici e per generare i grafici stessi.

È possibile generare grafici riguardanti:

- l'andamento del costo di `mint` al crescere della dimensione della collezione di *token*, con i relativi costi massimali ad ogni altezza del MMR;
- l'andamento del costo di `verify` al crescere della dimensione della collezione di *token`, con i relativi costi massimali ad ogni altezza del MMR;

Inoltre, per ogni collezione di cui si fornisce il file `data/collections/transfers/<collection_name>.csv` è possibile generare i grafici relativi al costo di `mint` e `verify`, in base ai trasferimenti effettuati: per ogni nuovo *token* generato, viene addizionato il costo di `mint` e per ogni *token* trasferito viene addizionato il costo di `verify`.

Per generare ogni grafico, è necessario prima creare l'ambiente di esecuzione e installare le dipendenze necessarie.

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

Per generare i grafici è sufficiente eseguire il seguente comando.

```bash
$ make
```