#########################################################################################
## MySQLdb Parser
## Purpose: To take in a .fasta file ofprotein data, acces mysql UCSC web server
## to match protein sequence and get protID, use to access all relevant
## coordinate and coding information in knownGene table
## Author: kjwade
## Created: 4/15/2015
############################################################################################

import sys
import MySQLdb
from collections import defaultdict
def main():
    seqs = get_data()
    access_mysql(seqs)
    
## Returns: dictionary of sequence data from input file: Keys= gene ID, values= sequence
def get_data():
    seq_data =defaultdict(str)
    seq_string = ''
    infile = open(sys.argv[1],'r')
    for line in infile:
        seq_string += line
    seqs = seq_string.split('>')
    for gene in seqs[1:]:
        gene =gene.split('\n')
        protseq=gene[1].strip()
        seq_data[gene[0].strip()]+= protseq
   
    return seq_data


## Creates mySQL server object to iterate through sequence dictionary, search for corresponding UCSC, hg19 sequence ID in knownGene table
## Writes hg19 geneID, gene name, chrom#, strand, transcription start, transcription end, cds start, cds end, exon 
## count, exons starts, exon ends, proteinID, alignID to output file --> human_aa_data.txt    
def access_mysql(seqs):
    outfile = open('human_aa_data.txt','w')
    outfile.write("ID\tname\tchrom\tstrand\ttxStart\ttxEnd\tcdsStart\tcdsEnd\texonCount\texonStarts\texonEnds\tproteinID\talignID\n")
    hg19 = MySQLdb.connect(host="genome-mysql.cse.ucsc.edu", user="genome", passwd="", db="hg19")
    cur = hg19.cursor() # Create Cursor object to execute queries
    for key in seqs:
        print seqs[key]
        try:
            cur.execute("""SELECT name FROM knownGenePep WHERE seq =%s""" , (seqs[key],))  # Identifies and stores proteinID of given amino acid sequence as variable prot_id
            prot_id = cur.fetchone()
            cur.execute("""SELECT * FROM knownGene WHERE name =%s""" ,(prot_id,)) # Searches for geneID that corresponds to the protID
            data = cur.fetchone()
            outfile.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (key.strip(),data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9],data[10],data[11]))
        except:
            print "Error: Could not find protein sequence match for ",key
            pass
    hg19.close()
    outfile.close()
                   
main()
