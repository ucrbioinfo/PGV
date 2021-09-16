import argparse
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

BLOCK_TYPES = {
    "core": "C",
    "dispensable": "D",
    "unique": "U"
}


def extract_seq_for_blocks():
    parser = argparse.ArgumentParser(description='Utility to extract block sequences from pan-genomes')
    parser.add_argument('--genome', '-g', dest='genome', required=True,
                        help='genome fasta file to extract sequence from')
    parser.add_argument('--bed_file', '-bed', dest='bed', required=True,
                        help='bed file of blocks')
    parser.add_argument('--block_type', '-block', dest='block', required=True,
                        help='block type')
    parser.add_argument('--out', '-o', dest='output', required=True,
                        help='output file for block sequences')

    args = parser.parse_args()
    genome = args.genome
    bed_file = args.bed
    block_type = args.block
    output_file = args.output
    print(genome, bed_file, block_type, output_file)

    if block_type not in BLOCK_TYPES:
        raise ValueError(
            "Block type %s is not supported. Please choose from: %s",
            block_type,
            list(BLOCK_TYPES.keys())
        )
    with open(genome, "r") as input_fasta:
        seqs = SeqIO.parse(input_fasta, "fasta")
        genome_seqs = {seq.name: seq for seq in seqs}

    with open(bed_file, "r") as input_bed:
        res = []
        for line in input_bed:
            infos = line.rstrip().split("\t")
            chr = infos[0]
            start = int(infos[1])
            end = int(infos[2])
            block_name = infos[3]
            if chr not in genome_seqs:
                raise ValueError(
                    "%s is not in input genome %s",
                    chr,
                    genome,
                )

            if block_name.startswith(BLOCK_TYPES[block_type]):
                record = SeqRecord(
                    genome_seqs[chr].seq[start-1: end],
                    id=block_name,
                    name=block_name,
                    description=f"[{block_type}]"
                )
                res.append(record)

    SeqIO.write(res, output_file, "fasta")


if __name__ == "__main__":
    extract_seq_for_blocks()