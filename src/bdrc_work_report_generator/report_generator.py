import csv
import logging
import re
import pyewts
import uuid
import yaml
from pathlib import Path
from rdflib import URIRef, Literal, BNode, Graph
from rdflib.namespace import RDF, RDFS, SKOS, OWL, Namespace, NamespaceManager, XSD

BDR = Namespace("http://purl.bdrc.io/resource/")
BDO = Namespace("http://purl.bdrc.io/ontology/core/")
BDA = Namespace("http://purl.bdrc.io/admindata/")
ADM = Namespace("http://purl.bdrc.io/ontology/admin/")
EWTSCONV = pyewts.pyewts()


def ewtstobo(ewtsstr):
    """Convert wylie tibetan to unicode tibetan character.

    Args:
        ewtsstr (str): wylie tibetan string

    Returns:
        str: equivalent unicode tibetan character of wylie transliteration
    """
    res = EWTSCONV.toUnicode(ewtsstr)
    return res

def get_value(URI):
    """Extract value from URI.

    Args:
        URI (str): URI

    Returns:
        str: value from URI
    """
    return URI.split("/")[-1]

def parse_volumes(volumes):
    total_number_of_page = 0
    total_number_of_volume = 0
    for volume in volumes:
        volume_id = get_value(str(volume))
        volume_graph = Graph()
        volume_graph.parse(f"https://ldspdi.bdrc.io/resource/{volume_id}.ttl")
        total_number_of_page += int(volume_graph.value(BDR[volume_id], BDO['volumePagesTotal']))
        total_number_of_volume += 1
    return total_number_of_volume, total_number_of_page

def get_work_report(work_id):
    work_report = {
        'work_id': work_id,
        'Number_of_Volumes': None,
        'Number_of_Pages': None
    }
    work_graph = Graph()
    work_graph.parse(f"https://ldspdi.bdrc.io/resource/{work_id}.ttl")
    volumes = work_graph.objects(BDR[work_id], BDO['instanceHasVolume'])
    number_of_volumes, total_page_number = parse_volumes(volumes)
    work_report['Number_of_Volumes'] = number_of_volumes
    work_report['Number_of_Pages'] = total_page_number
    return work_report

def get_csv_report(work_ids, output_dir):
    csv_report = "work_id, Number_of_volumes, Number_of_pages\n"
    for work_id in work_ids:
        work_report = get_work_report(work_id)
        csv_report += f"{work_report['work_id'], work_report['Number_of_Volumes'], work_report['Number_of_page']}\n"
    (output_dir / "work_report.csv").write_text(csv_report, encoding='utf-8')


if __name__ == "__main__":
    work_ids = Path('./data/work_id.txt').read_text(encoding='utf-8').splitlines()
    get_csv_report(work_ids, output_dir=Path('./data/'))