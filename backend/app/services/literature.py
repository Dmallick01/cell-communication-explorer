"""PubMed literature lookup via NCBI E-utilities (no API key required)."""

from __future__ import annotations

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any


def _fetch_pubmed_ids(query: str, max_results: int = 5) -> list[str]:
    params = urllib.parse.urlencode(
        {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "tool": "cell_communication_explorer",
            "email": "cce@example.com",
        }
    )
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        import json

        data = json.loads(resp.read().decode())
    return data.get("esearchresult", {}).get("idlist", [])


def _fetch_pubmed_summaries(pmids: list[str]) -> list[dict[str, Any]]:
    if not pmids:
        return []

    params = urllib.parse.urlencode(
        {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "tool": "cell_communication_explorer",
            "email": "cce@example.com",
        }
    )
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{params}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        root = ET.fromstring(resp.read())

    papers = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID") or ""
        title = article.findtext(".//ArticleTitle") or ""
        journal = article.findtext(".//Journal/Title") or ""
        year = article.findtext(".//PubDate/Year") or ""
        authors = []
        for au in article.findall(".//Author"):
            last = au.findtext("LastName") or ""
            fore = au.findtext("ForeName") or ""
            if last:
                authors.append(f"{last} {fore}".strip())
        papers.append(
            {
                "pmid": pmid,
                "title": title,
                "journal": journal,
                "year": year,
                "authors": authors[:4],
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            }
        )
    return papers


def search_edge_literature(
    ligand: str,
    receptor: str,
    source_cell_type: str,
    target_cell_type: str,
    max_results: int = 4,
) -> list[dict[str, Any]]:
    queries = [
        f'"{ligand}" "{receptor}" cell communication',
        f'"{ligand}" ligand "{receptor}" receptor single cell',
        f'"{source_cell_type}" "{target_cell_type}" {ligand} signaling',
    ]
    seen: set[str] = set()
    papers: list[dict[str, Any]] = []
    for q in queries:
        for pmid in _fetch_pubmed_ids(q, max_results=max_results):
            if pmid in seen:
                continue
            seen.add(pmid)
        if len(seen) >= max_results:
            break

    if seen:
        papers = _fetch_pubmed_summaries(list(seen)[:max_results])

    for p in papers:
        p["query_context"] = f"{ligand}→{receptor} ({source_cell_type}→{target_cell_type})"
    return papers


def literature_for_edges(edges: list[dict[str, Any]], max_edges: int = 8) -> list[dict[str, Any]]:
    """Attach PubMed hits to top communication edges."""
    out = []
    for edge in edges[:max_edges]:
        papers = search_edge_literature(
            edge.get("ligand", ""),
            edge.get("receptor", ""),
            edge.get("source_cell_type", ""),
            edge.get("target_cell_type", ""),
        )
        out.append({**edge, "papers": papers})
    return out
