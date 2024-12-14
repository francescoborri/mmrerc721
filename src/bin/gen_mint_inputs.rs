use mmr::{proof::Proof, MMR};
use std::{
    env::args,
    fs::{File, OpenOptions},
    io::{Result, Write},
    process::exit,
};

fn main() -> Result<()> {
    let args = args().collect::<Vec<String>>();

    if args.len() != 4 {
        eprintln!(
            "Usage: {} <out_file_path> <num_tokens> <to_address>",
            args[0]
        );
        exit(1);
    }

    let out_file_path = &args[1];
    let num_tokens = args[2].parse::<u64>().expect("invalid num_tokens");
    let to_address = &args[3];

    if num_tokens == 0 {
        eprintln!("num_tokens must be greater than 0");
        exit(1);
    }

    let mut out_file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(out_file_path)?;

    let mut mmr = MMR::new(1.into());
    let mut prev_root = mmr.root();

    let first_item_proof = mmr.gen_proof(0);
    write_line(
        &mut out_file,
        to_address,
        &Proof::default(),
        &first_item_proof,
    )?;

    for token_num in 2..=num_tokens {
        mmr.append(token_num.into());

        let prev_token_proof = mmr.gen_proof(token_num - 2);
        let new_token_proof = mmr.gen_proof(token_num - 1);

        assert!(prev_token_proof.verify());
        assert!(new_token_proof.verify());
        assert!(prev_token_proof.verify_ancestor(prev_root));

        write_line(
            &mut out_file,
            to_address,
            &prev_token_proof,
            &new_token_proof,
        )?;

        prev_root = mmr.root();
    }

    Ok(())
}

fn write_line(
    out_file: &mut File,
    to_address: &String,
    prev_token_proof: &Proof,
    new_token_proof: &Proof,
) -> Result<()> {
    writeln!(
        out_file,
        "\"{}\",{},{}",
        to_address, prev_token_proof, new_token_proof
    )
}
