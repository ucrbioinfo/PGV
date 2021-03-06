inputGenomes = ["sample/GCA_000001735.2_TAIR10.1_genomic.fna", "sample/GCA_001651475.1_Ler_Assembly_genomic.fna", "sample/GCA_900660825.1_Ath.Ler-0.MPIPZ.v1.0_genomic.fna"]

XMFAFile = "sample/output.xmfa"

numOfGenomes = 3
numOfChrms = 1
alnScoreThr = 0.5

BEDaligned = False  ## whether to align all C blocks
outBEDConsensus = "PGV.consensus.bed"

colorConsensus = "0,0,255"
colorC = "230,243,255"
colorCrev = "255,0,255"
colorCtrans = "0,0,255"
colorP = "0,255,0"
colorU = "255,0,0"
