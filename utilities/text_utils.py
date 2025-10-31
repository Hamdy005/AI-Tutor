import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredURLLoader

def text_from_pdf(pdf_file):

    reader = PyPDF2.PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        text += page.extract_text()

    return text


def chunk_text(text, chunk_size = 800, chunk_overlap = 150):
    
    splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap)
    chunks = splitter.split_text(text)
    return chunks 


def scrap_website(url):

    loader = UnstructuredURLLoader(urls = [url], ssl_verify = True)
    data = loader.load()
    text = data[0].page_content
    return text