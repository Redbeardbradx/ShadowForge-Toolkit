from typing import Optional, Dict
import requests
from typing import Optional
try:
    from stem import Signal
    from stem.control import Controller
    STEM_AVAILABLE = True
except ImportError:
    STEM_AVAILABLE = False
    print("[yellow]Stem not found—pip install stem for full TOR control. Fallback: SOCKS proxy.[/yellow]")

def tor_session(timeout: int = 30) -> requests.Session:
    """
    Forge TOR session. Assumes TOR running on 9050 (control 9051). Ethical: Local/VM tests only.
    Returns session w/ SOCKS5 proxy; renew_identity if stem.
    """
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    session.timeout = timeout

    if STEM_AVAILABLE:
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate()  # Default no pw; set CONTROL_PASSWORD in torrc
                controller.signal(Signal.NEWNYM)  # Fresh circuit
                session.tor_circuit_id = controller.get_info("circuit-status")[-1].id if controller.get_info("circuit-status") else "Unknown"
        except Exception as e:
            print(f"[red]TOR control failed: {e}—using static SOCKS.[/red]")

    return session

def anon_request(url: str, session: Optional[requests.Session] = None) -> Dict:
    """Veil a GET thru TOR. Returns JSON or error."""
    if session is None:
        session = tor_session()
    try:
        resp = session.get(url)
        return {"status": resp.status_code, "content": resp.json() if resp.headers.get('content-type') == 'application/json' else resp.text[:500]}
    except requests.RequestException as e:
        return {"error": f"Anon fetch failed: {str(e)}—check TOR service."}