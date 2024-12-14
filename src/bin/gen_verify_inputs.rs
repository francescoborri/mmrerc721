use mmr::{proof::Proof, MMR};
use std::{
    env::args,
    fs::{File, OpenOptions},
    io::{Result, Write},
    process::exit,
};

fn main() -> Result<()> {
    let args = args().collect::<Vec<String>>();

    if args.len() != 3 {
        eprintln!("Usage: {} <out_file_path> <num_tokens>", args[0]);
        exit(1);
    }

    let out_file_path = &args[1];
    let num_tokens = args[2].parse::<u64>().expect("invalid num_tokens");

    if num_tokens == 0 {
        eprintln!("num_tokens must be greater than 0");
        exit(1);
    }

    let mut out_file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(out_file_path)?;

    let mut mmr = MMR::new(1.into());

    let proof = mmr.gen_proof(0);
    write_line(&mut out_file, &proof)?;

    for token_num in 2..=num_tokens {
        mmr.append(token_num.into());

        let proof = mmr.gen_proof(0);
        assert!(proof.verify());

        write_line(&mut out_file, &proof)?;
    }

    Ok(())
}

fn write_line(out_file: &mut File, proof: &Proof) -> Result<()> {
    writeln!(out_file, "{}", proof)
}
