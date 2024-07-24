# Document Chunkers

A collection of helpers to process raw documents

## Overview

This library provides tools for chunking documents into manageable pieces such as paragraphs and sentences. It's particularly useful for preprocessing text data for natural language processing (NLP) tasks.

### Supported Models

![img.png](img.png)

- **SaT** &mdash; [Segment Any Text: A Universal Approach for Robust, Efficient and Adaptable Sentence Segmentation](https://arxiv.org/abs/2406.16678) by Markus Frohmann, Igor Sterner, Benjamin Minixhofer, Ivan Vulić and Markus Schedl (**state-of-the-art, encouraged**). - 85 languages
- **WtP** &mdash; [Where’s the Point? Self-Supervised Multilingual Punctuation-Agnostic Sentence Segmentation](https://aclanthology.org/2023.acl-long.398/) by Benjamin Minixhofer, Jonas Pfeiffer and Ivan Vulić. - 85 languages
- **PySBD** &mdash; [{P}y{SBD}: Pragmatic Sentence Boundary Disambiguation](https://arxiv.org/abs/2010.09657) by Nipun Sadvilkar and Mark Neumann  (rule-based, **lightweight**) - 22 languages

## Usage

### Example: Using SaT for Sentence Segmentation

```python
from ovos_document_chunkers import SaTSentenceSplitter

config = {"model": "sat-3l-sm", "use_cuda": False}
splitter = SaTSentenceSplitter(config)

text = "This is a sentence. And this is another one."
sentences = splitter.chunk(text)

for sentence in sentences:
    print(sentence)
```

### Example: Using WtP for Paragraph Segmentation

```python
from ovos_document_chunkers import WtPParagraphSplitter

config = {"model": "wtp-bert-mini", "use_cuda": False}
splitter = WtPParagraphSplitter(config)

text = "This is a paragraph. It contains multiple sentences.\n\nThis is another paragraph."
paragraphs = splitter.chunk(text)

for paragraph in paragraphs:
    print(paragraph)
```

### Example: Using PySBD for Sentence Segmentation

```python
from ovos_document_chunkers import PySBDSentenceSplitter

config = {"lang": "en"}
splitter = PySBDSentenceSplitter(config)

text = "This is a sentence. This is another one!"
sentences = splitter.chunk(text)

for sentence in sentences:
    print(sentence)
```

### Example using MarkdownSentenceSplitter

```python
from ovos_document_chunkers.text.markdown import MarkdownSentenceSplitter 
import requests

markdown_text = requests.get("https://github.com/OpenVoiceOS/ovos-core/raw/dev/README.md").text

sentence_splitter = MarkdownSentenceSplitter()
sentences = sentence_splitter.chunk(markdown_text)

print("Sentences:")
for sentence in sentences:
    print(sentence)
```

### Example using MarkdownParagraphSplitter
```python
from ovos_document_chunkers.text.markdown import MarkdownParagraphSplitter
import requests

markdown_text = requests.get("https://github.com/OpenVoiceOS/ovos-core/raw/dev/README.md").text

paragraph_splitter = MarkdownParagraphSplitter()
paragraphs = paragraph_splitter.chunk(markdown_text)

print("\nParagraphs:")
for paragraph in paragraphs:
    print(paragraph)
```

### Example using HTMLSentenceSplitter

```python
from ovos_document_chunkers import HTMLSentenceSplitter
import requests

html_text = requests.get("https://www.gofundme.com/f/openvoiceos").text

sentence_splitter = HTMLSentenceSplitter()
sentences = sentence_splitter.chunk(html_text)

print("Sentences:")
for sentence in sentences:
    print(sentence)
```

### Example using HTMLParagraphSplitter

```python
from ovos_document_chunkers import HTMLParagraphSplitter
import requests

html_text = requests.get("https://www.gofundme.com/f/openvoiceos").text

paragraph_splitter = HTMLParagraphSplitter()
paragraphs = paragraph_splitter.chunk(html_text)

print("\nParagraphs:")
for paragraph in paragraphs:
    print(paragraph)
```