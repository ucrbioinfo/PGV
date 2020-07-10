MauveExecutable = "/home/qliang/0.soft/Mauve/mauve_snapshot_2015-02-13/linux-x64/progressiveMauve"
inputGenomes = ["data/Cowpea_Genome_1.0.fasta", "data/cowpea_A.fasta", "data/cowpea_B.fasta", "data/cowpea_C.fasta", "data/cowpea_D.fasta", "data/cowpea_E.fasta", "data/cowpea_F.fasta"]

XMFAFile = "data/output.xmfa"

numOfGenomes = len(inputGenomes)
numOfChrms = 11
alnScoreThr = 0.7

BEDaligned = True  ## whether to align all C blocks
outBEDConsensus = "PGV.consensus.bed"

colorConsensus = "0,0,255"
colorC = "230,243,255"
colorCrev = "255,0,255"
colorCtrans = "0,0,255"
colorP = "0,255,0"
colorU = "255,0,0"
