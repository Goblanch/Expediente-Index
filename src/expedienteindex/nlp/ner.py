from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Optional, Dict, Any
import re

try:
    import spacy
    from spacy.language import Language
except Exception as e:
    spacy = None
    Language = None

# --- Patrones España: DNI / NIE
_DNI_RE = re.compile(r"\b(?P<dni>\d{8})(?P<letter>[A-HJ-NP-TV-Z])\b", re.IGNORECASE)
_NIE_RE = re.compile(r"\b(?P<nie>[XYZxyz])\d{7}(?P<letter>[A-HJ-NP-TV-Z])\b", re.IGNORECASE)

# --- emails y teléfonos
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"""
    (?<!\w)                              # límite izquierdo laxo (no letra/num)
    (?:\+\d{1,3}[\s\-.]?)?               # prefijo internacional opcional (+1, +34, +351, etc.)
    (?:\(?\d{1,4}\)?[\s\-.]?){2,6}       # 2 a 6 grupos de 1-4 dígitos con separadores
    \d                                   # termina en dígito
    (?!\w)                               # límite derecho laxo
""", re.VERBOSE)

@dataclass
class DetectedEntity:
    text: str
    start: int
    end: int
    label: str
    source: str
    meta: Optional[Dict[str, Any]] = None

class NEREngine:
    def __init__(self, lang: str = "es", prefer_small: bool = False) -> None:
        self.lang = lang
        self.prefer_small = prefer_small
        self._nlp: Optional["Language"] = None

    def load(self) -> None:
        if spacy is None:
            raise RuntimeError(
                "spaCy no está instalado. Instala 'spacy' y descarga un modelo: "
                "python -m spacy download es_core_news_md"
            )
        if self._nlp is not None:
            return
        
        # Orden de preferencias de modelos
        candidates = []
        if self.lang.startswith("es"):
            if self.prefer_small:
                candidates = ["es_core_news_sm", "es_core_news_md", "es_core_news_lg"]
            else:
                candidates = ["es_core_news_md", "es_core_news_sm", "es_core_news_lg"]
        else:
            # fallback genérico si se usa otro idioma
            candidates = [f"{self.lang}_core_news_md", f"{self.lang}_core_news_sm"]

        last_err: Optional[Exception] = None
        for name in candidates:
            try:
                self._nlp = spacy.load(name)
                break
            except Exception as e:
                last_err = e
                continue
        
        if self._nlp is None:
            raise RuntimeError(
                f"No se pudo cargar un modelo spaCy para '{self.lang}'. "
                f"Intentandos: {candidates}. Último error: {last_err}"
            )

    def _spacy_entities(self, text: str) -> List[DetectedEntity]:
        assert self._nlp is not None
        doc = self._nlp(text)
        ents: List[DetectedEntity] = []

        label_map = {
            "PER": "PERSON",
            "PERSON": "PERSON",
            "ORG": "ORG",
            "LOC": "LOC",
            "GPE": "LOC",
            "MISC": "MISC",
            "DATE": "DATE",
            "TIME": "TIME",
            "NORP": "MISC",  # nacionalidades/grupos
            "CARDINAL": "NUMBER",
            "QUANTITY": "NUMBER",
            "ORDINAL": "NUMBER",
            "LAW": "LAW",
        }
        for ent in doc.ents:
            label = label_map.get(ent.label_, ent.label_)
            ents.append(
                DetectedEntity(
                    text=ent.text,
                    start=ent.start_char,
                    end=ent.end_char,
                    label=label,
                    source="spacy",
                )
            )

        return ents

    def _regex_entities(self, text: str, include_email_phone: bool = False) -> List[DetectedEntity]:
        ents: List[DetectedEntity] = []
        # DNI
        for m in _DNI_RE.finditer(text):
            ents.append(
                DetectedEntity(
                    text=m.group(0),
                    start=m.start(),
                    end=m.end(),
                    label="ID_NUMBER",
                    source="regex",
                    meta={"type": "DNI"}
                )
            )
        # NIE
        for m in _NIE_RE.finditer(text):
            ents.append(
                DetectedEntity(
                    text=m.group(0),
                    start=m.start(),
                    end=m.end(),
                    label="ID_NUMBER",
                    source="regex",
                    meta={"type": "NIE"}
                )
            )
        
        if include_email_phone:
            for m in _EMAIL_RE.finditer(text):
                ents.append(
                    DetectedEntity(
                        text=m.group(0),
                        start=m.start(),
                        end=m.end(),
                        label="EMAIL",
                        source="regex"
                    )
                )
            for m in _PHONE_RE.finditer(text):
                ents.append(
                    DetectedEntity(
                        text=m.group(0),
                        start=m.start(),
                        end=m.end(),
                        label="PHONE",
                        source="regex"
                    )
                )
        return ents

    def detect(self, text: str, *, use_regex: bool = True, include_email_phone: bool = False) -> List[DetectedEntity]:
        self.load()
        results = []
        results.extend(self._spacy_entities(text))
        if use_regex:
            results.extend(self._regex_entities(text, include_email_phone=include_email_phone))

        # Ordenamos por posición en texto
        results.sort(key=lambda e: (e.start, e.end))
        return results

# Test cases
TEXTO = "El Sr. Iván Castillo Mendoza con DNI 01647550Z es culpable de estafar a Empresa S.L. con número de teléfono +51 68639912 y correo correo@gmail.com"
ner = NEREngine()
print(ner.detect(TEXTO, include_email_phone=True))