## Generazione di MMR *proof* consecutivi per `mint`

Per generare MMR *proof* consecutivi per $n$ elementi, per poi essere passati come input a più chiamate consecutive di `mint`, si usa il seguente comando.

```bash
$ cargo run --bin gen_mint_inputs -- <out_file_path> <n> <to_address>
```

Il comando genera $2n$ MMR *proof*, e li scrive nel file `out_file_path`, inserendo $2$ MMR *proof* per ogni riga. Alla riga $1\leq i \leq n$ saranno presenti il MMR proof per l'elemento $i-1$ (`prevTokenProof`) e l'elemento $i$ (`nextTokenProof`).

La prima `mint` non verifica `prevTokenProof`, in quanto non c'è ancora alcun *token*, per cui il *proof* per l'elemento $0$ ha valori arbitrari che verranno ignorati.

I `tokenId` dei *token* generati sono $1\ldots n$ e non tutti $0$ per evitare che `mint` fallisca a causa di *token* duplicati.

In cima a ogni riga viene inoltre aggiunto il valore di `<to_address>`, ossia l'indirizzo a cui inviare i *token* generati, così da far combaciare ogni riga con i parametri di `mint`. `<to_address>` è una stringa esadecimale che inizia con `0x` e rappresenta un indirizzo Ethereum.

## Generazione di MMR *proof* per `verify`

Il seguente comando permette di generare il MMR proof con dimensione massima per ogni MMR con dimensione da 1 a $n$.

```bash
$ cargo run --bin gen_verify_inputs -- <out_file_path> <n>
```

Il comando genera $n$ MMR proof e li scrive nel file `out_file_path`, uno per riga. Il MMR proof alla riga $i$ è relativo alla prima foglia del MMR con $i$ elementi inseriti.