import os
import requests
from crewai_tools import tool
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

@tool("Upload to Google Drive")
def upload_to_drive(file_name: str, content: str) -> str:
    """Utilise cet outil pour sauvegarder un fichier Markdown dans le Google Drive de l'utilisateur."""
    try:
        service = get_drive_service()
        file_metadata = {'name': file_name, 'mimeType': 'text/markdown'}
        fh = io.BytesIO(content.encode('utf-8'))
        media = MediaIoBaseUpload(fh, mimetype='text/markdown', resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        return f"Succès ! Fichier sauvegardé sur Drive. Lien: {file.get('webViewLink')}"
    except Exception as e:
        return f"Erreur lors de la sauvegarde: {str(e)}"

@tool("Search Semantic Scholar")
def search_academic_papers(query: str, limit: int = 5) -> str:
    """Utilise cet outil pour chercher des articles scientifiques Peer-Reviewed."""
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={limit}&fields=title,authors,year,abstract,url"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results = ""
        for paper in data.get('data', []):
            authors = ", ".join([a['name'] for a in paper.get('authors', [])])
            results += f"Titre: {paper.get('title')}\nAnnée: {paper.get('year')}\nAuteurs: {authors}\nAbstract: {paper.get('abstract')}\nLien: {paper.get('url')}\n\n---\n"
        return results
    return "Erreur lors de la recherche d'articles."