import socket
import subprocess
import paramiko

def check_open_ports(host, ports):
    open_ports = []
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((host, port))
                open_ports.append(port)
        except:
            pass
    return open_ports

def check_outdated_software():
    outdated_software = {}

    # Check for outdated software using 'apt-get' (Ubuntu/Debian-based systems)
    try:
        apt_outdated = subprocess.check_output(['apt-get', '--just-print', 'upgrade'])
        apt_outdated = apt_outdated.decode('utf-8').strip().split('\n')
        for line in apt_outdated:
            if "Inst " in line:
                package_name = line.split()[1]
                outdated_software[package_name] = 'apt'
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Check for outdated software using 'dnf' (Red Hat/CentOS-based systems)
    try:
        dnf_outdated = subprocess.check_output(['dnf', 'list', 'updates', '-q'])
        dnf_outdated = dnf_outdated.decode('utf-8').strip().split('\n')[1:]
        for package_info in dnf_outdated:
            package_name, _ = package_info.split()
            outdated_software[package_name] = 'dnf'
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Check for outdated Python packages using 'pip'
    try:
        pip_outdated = subprocess.check_output(['pip', 'list', '--outdated', '-q'])
        pip_outdated = pip_outdated.decode('utf-8').strip().split('\n')[2:]
        for package_info in pip_outdated:
            package_name, _, _, _ = package_info.split()
            outdated_software[package_name] = 'pip'
    except subprocess.CalledProcessError:
        pass

    return outdated_software

def check_weak_passwords(hostname, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, username=username, password=password, timeout=5)
        return True
    except:
        return False
    finally:
        ssh.close()

def main():
    # Get user inputs
    target_host = input("Enter the target host: ")
    target_ports = [int(port) for port in input("Enter target ports (comma-separated): ").split(",")]

    print("Running RapidSecure Scan on:", target_host)

    # Check open ports
    open_ports = check_open_ports(target_host, target_ports)
    print("Open ports:", open_ports)

    # Check for outdated software
    outdated_packages = check_outdated_software()
    if outdated_packages:
        print("Outdated software:")
        for package, package_manager in outdated_packages.items():
            print(f"{package} (managed by {package_manager})")
    else:
        print("No outdated software found.")

    # Check for weak passwords (example)
    target_username = input("Enter the target username: ")
    target_passwords = input("Enter target passwords (comma-separated): ").split(",")

    for password in target_passwords:
        if check_weak_passwords(target_host, target_username, password):
            print(f"Weak password found: {password}")
            break
    else:
        print("No weak passwords found.")

if __name__ == "__main__":
    main()
