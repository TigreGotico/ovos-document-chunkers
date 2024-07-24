import os
import re
from typing import Iterable, Dict, Optional, List, Any

import requests
from ovos_document_chunkers.base import AbstractTextDocumentChunker
from quebra_frases import sentence_tokenize


class HTMLSentenceSplitter(AbstractTextDocumentChunker):
    """
    A sentence splitter for HTML documents.

    This splitter breaks down HTML documents into sentences by first
    converting HTML content into paragraphs and then splitting those
    paragraphs into sentences.

    Attributes:
        config (Dict[str, Any]): Configuration dictionary for the splitter.
        splitter (HTMLParagraphSplitter): Instance of HTMLParagraphSplitter to handle paragraph splitting.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the splitter with a configuration.

        Args:
            config (Optional[Dict[str, Any]]): Configuration dictionary for the splitter.
                                                 Defaults to an empty dictionary if None.
        """
        config = config or {}
        super().__init__(config)
        self.splitter = HTMLParagraphSplitter(self.config)

    def chunk(self, data: str) -> Iterable[str]:
        """
        Split the input HTML text into sentences.

        Args:
            data (str): The HTML text to split.

        Returns:
            Iterable[str]: An iterable of sentences.
        """
        for chunk in self.splitter.chunk(data):
            for p in chunk.split("\n"):
                for s in sentence_tokenize(p):
                    if s and len(s.split()) > 4:
                        yield s.strip()


class HTMLParagraphSplitter(AbstractTextDocumentChunker):
    """
    A paragraph splitter for HTML documents.

    This splitter breaks down HTML documents into paragraphs by cleaning
    the HTML content and removing unnecessary tags and attributes.

    Attributes:
        config (Dict[str, Any]): Configuration dictionary for the splitter.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the splitter with a configuration.

        Args:
            config (Optional[Dict[str, Any]]): Configuration dictionary for the splitter.
                                                 Defaults to an empty dictionary if None.
        """
        config = config or {}
        super().__init__(config)

    def chunk(self, data: str) -> Iterable[str]:
        """
        Split the input HTML text into paragraphs.

        Args:
            data (str): The HTML text to split.

        Returns:
            Iterable[str]: An iterable of paragraphs.
        """
        return denoise_html(data)


def denoise_html(html_content: str,
                 bad_words: Optional[List[str]] = None,
                 stop_words: Optional[List[str]] = None,
                 min_words: int = 5) -> List[str]:
    """
    Clean the HTML content by removing all tags except for <div>, <h>, <p>, and <br> tags.
    Also removes <script> and <style> tags along with their content.

    Args:
        html_content (str): The HTML content to clean.
        bad_words (Optional[List[str]]): List of words that, if found, will cause the line to be skipped.
        stop_words (Optional[List[str]]): List of common stop words to ignore when processing the content.
        min_words (int): Minimum number of words a line must have to be included in the output.

    Returns:
        List[str]: The cleaned text content with only the allowed HTML tags.
    """
    if html_content.startswith("http"):
        response = requests.get(html_content)
        response.raise_for_status()  # Raise an error for bad status codes
        html_content = response.text

    if os.path.isfile(html_content) and html_content.endswith(".html"):
        with open(html_content) as f:
            html_content = f.read()

    # Default values for bad_words and stop_words
    bad_words = bad_words or ["cookie"]
    # ignore in word count
    stop_words = stop_words or ["the", "a", "an", "to", "of", "for", "as", "and", "it", "in", "we", "i"]

    # Remove <script> and <style> tags and their content
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.IGNORECASE | re.DOTALL)

    # Remove unwanted tags, keeping <div>, <h1> to <h6>, <p>, <br>
    clean_tags = re.compile(r'</?(div|h[1-6]|p|br)\b[^>]*>', re.IGNORECASE)
    cleaned_html = re.sub(r'</?[^>]*>', lambda m: m.group(0) if clean_tags.match(m.group(0)) else '', html_content,
                          flags=re.IGNORECASE | re.DOTALL)

    # Remove attributes from allowed tags
    tag_cleaner = re.compile(r'<(/?\w+)([^>]*)>', re.IGNORECASE)
    cleaned_html = re.sub(tag_cleaner, lambda m: f"<{m.group(1)}>", cleaned_html)

    # Replace <div> and <br> tags with newlines
    cleaned_html = re.sub(r'<div[^>]*>', '\n', cleaned_html, flags=re.IGNORECASE)
    cleaned_html = re.sub(r'</div>', '\n', cleaned_html, flags=re.IGNORECASE)
    cleaned_html = re.sub(r'<br\s*/?>', '\n', cleaned_html, flags=re.IGNORECASE)

    # Replace headers with \n\n{header}
    for header_tag in range(1, 7):
        header_pattern = re.compile(rf'<h{header_tag}[^>]*>(.*?)</h{header_tag}>', re.IGNORECASE)
        cleaned_html = re.sub(header_pattern, lambda m: f'\n\n{m.group(1)}', cleaned_html)

    # Replace paragraphs with \n\n
    cleaned_html = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\n\1', cleaned_html, flags=re.IGNORECASE)

    lines = []
    for l in cleaned_html.split("\n"):
        words = [w for w in l.split() if w.lower() not in stop_words]
        lnorm = " ".join(words)
        if l == "\n":
            lines.append(l)
            continue
        if any([w in l.lower() for w in bad_words]):
            continue
        elif len(lnorm.split()) < min_words:
            lines.append("\n")
        else:
            lines.append(l)

    cleaned_html = "\n".join(lines)
    return [l.strip() for l in cleaned_html.split("\n\n\n") if l.strip()]


if __name__ == "__main__":

    # Example usage of HTMLParagraphSplitter
    paragraph_splitter = HTMLParagraphSplitter()
    paragraphs = list(paragraph_splitter.chunk("https://www.gofundme.com/f/openvoiceos"))
    print(f"Number of paragraphs: {len(paragraphs)}")
    # Number of paragraphs: 30

    # Example usage of HTMLSentenceSplitter
    sentence_splitter = HTMLSentenceSplitter()
    sentences = list(sentence_splitter.chunk("https://www.gofundme.com/f/openvoiceos"))
    print(f"Number of sentences: {len(sentences)}")
    # Number of sentences: 55

    for sentence in sentences:
        print(sentence)
    # Fundraiser by Peter Steenbergen : Support OpenVoiceOS as Nonprofit Foundation
    # raised of €6,500 goal • 105 donations
    # Peter Steenbergen and 3 others are organizing this fundraiser.
    # Giving Voice to the Future: Support OpenVoiceOS in Establishing a Nonprofit association.
    # OpenVoiceOS (OVOS) is a collective of programmers and hardware enthusiasts who produce an open-source voice assistant.
    # Our core team began in 2019-2020 as an offshoot of the Mycroft community, bringing a handful of third-party projects under one roof.
    # One of those projects was an extension of Mycroft itself, which slowly became independent of its parent.
    # Some years later, our assistant is brimming with added features, and we maintain an extensive catalog of related software.
    # We've been positioned to do this, in part, because the team consists of well-known Mycroft contributors, several of whom work or have worked on Mycroft-derived projects for a living.
    # Our credibility within the Mycroft community helped us attract a small but dedicated community of our own, and we've been operating at a comfortable scale ever since.
    # In the early 2020s, Mycroft's first-party codebase began to stale, as its developers became increasingly focused on a bespoke implementation for their Mark II smart speaker.
    # Other Mycroft implementations - some commercial, some run by open-source communities - began to struggle with Mycroft's stale codebase, and several turned to us for an actively-maintained alternative.
    # With their employers' consent, those of us paid to work on relevant projects migrated to OVOS, which enabled those members to spend company time on our open-source projects.
    # In this roundabout fashion, the OVOS assistant, which will receive a name of its own in the coming weeks, became an accidental fork of Mycroft.
    # We've been operating in this manner for over two years, without giving the arrangement much thought.
    # At OpenVoiceOS, we envision a world where technology empowers individuals to navigate their daily lives with privacy, security, and ease.
    # Our vision is to create a fully community-driven, open-source, privacy-respecting voice assistant that puts users in control of their data and empowers them to interact with their technology in a way that feels natural and intuitive.
    # We believe that by collaborating with a diverse range of contributors, we can create an accessible and inclusive platform that supports a wide range of languages and abilities.
    # Through transparency and ethical practices, we aim to promote trust and confidence in the tech industry and to provide a platform that empowers individuals to navigate their digital lives with ease and security.
    # We welcome and encourage both commercial and nonprofit organizations to build on top of our software, and we’re prepared to help, as long as they share our commitment to privacy and user control.
    # With MycroftAI reduced to a skeleton crew, and the transfer of most development operations to Neon, our ecosystem has been abruptly reduced to projects which had already switched to our code.
    # Neon derives from our code.
    # KDE derives from our code.
    # We are aware of no other Mycroft-based projects in production.
    # If Neon represents the future of Mycroft's commercial operations, OpenVoiceOS represents the survival of the adjacent open-source community, and our maintained code is every project's best hope for the future.
    # Circumstances have made it abundantly clear that, although we're fortunate to enjoy an extremely friendly relationship with our members' employers, we're just as fortunate to have endured this period intact.
    # Such an informal relationship with the world at large is no longer tenable.
    # We have no security while we exist at someone else's behest, and our colleagues have little to work with, because, on paper, we barely exist at all.
    # We're also compelled to recognize that our software is not in a very professional state at this moment.
    # A permanent solution means we need more structure than we've previously enjoyed and more help.
    # Though we are a community of volunteers, a larger and more structured team has greater and more expensive infrastructural needs.
    # Thus, both for our purposes and to coexist on a more equal footing with other entities, it seems necessary to formalize our existence as a not-for-profit, community-driven organization.
    # We will each, in our individual capacities, turn over those intellectual properties, such as branded art, logos, and domain names, which we have previously created on OVOS’ behalf, to the organization.
    # It will become the guarantor of our open-source voice assistant, independent of and separate from any dependent businesses.
    # Our assistant must stand on its own, as software, as a product, and financially; our relationships with other projects should resemble a definitive upstream/downstream position.
    # Projects based on our software should be able to advertise themselves as such, without explaining what they mean.
    # In taking these steps, we intend to safeguard our future as a group, and our software's future as a collaborative project.
    # We've decided to become a nonprofit association under Dutch law.
    # In the process, we will incur certain expenses.
    # We're sincerely grateful for any financial support.
    # Our belief and expectation is that a dedicated entity, designed to outlive our individual participation, is the best way to ensure that our software will be maintained indefinitely and in line with our values.
    # OpenVoiceOS will be registered as OpenVoiceOS V.z.w. (Dutch: "Vereninging zonder winstoogmerk", a nonprofit association, as distinguished from a foundation.) The association will support the OVOS community in legal and financial matters by securing donations of cash, hardware, and other relevant aid.
    # These donations will be used to facilitate software development, promotion, and support.
    # * Memorandum of association, notarized: €490
    # * Chamber of Commerce registration: €115
    # - Operating expenses, up-front for the first year:
    # * Runway for initial operations: €1900
    # This brings us to a total of €2889
    # Allowing for fees, our fundraising target is €3033
    # More information about our project can be found at the following places online:
    # If you want to speak with us, we are very active on our Matrix channels and more than happy to answer any questions you may have.
    # Fundraising team: OpenVoiceOS - Board Members (4)
    # Your easy, powerful, and trusted home for help
    # Send help right to the people and causes you care about
    # Your donation is protected by the GoFundMe Giving Guarantee
