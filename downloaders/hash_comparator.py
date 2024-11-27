import os
import hashlib

def calculate_hash(file_path):
    """Calcula el hash SHA-256 de un archivo."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            hash_sha256.update(byte_block)
    return hash_sha256.hexdigest()

def compare_hashes(dir1, dir2):
    """Compara los hashes de los archivos en dir1 con los archivos en dir2."""
    hashes_dir2 = {}

    # Calcular hashes de los archivos en dir2
    for root, _, files in os.walk(dir2):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = calculate_hash(file_path)
            hashes_dir2[file_hash] = file_path

    # Comparar con los archivos en dir1
    for root, _, files in os.walk(dir1):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = calculate_hash(file_path)
            if file_hash in hashes_dir2:
                print(f"Archivo encontrado con el mismo hash: {file_path} <-> {hashes_dir2[file_hash]}")
                os.remove(file_path)
                print(f"Archivo eliminado: {file_path}")

if __name__ == "__main__":
    #dir1 = input("Ingrese la ruta del primer directorio: ")
    #dir2 = input("Ingrese la ruta del segundo directorio: ")
    dir1 = "C:\\Users\\KyshinoDesktop\\Desktop\\ImageSpinesTool\\downloaded_spines"
    dir2 = "C:\\Users\\KyshinoDesktop\\Downloads\\Switch Spines Database-20241029T191356Z-001\\Switch Spines Database"
    compare_hashes(dir1, dir2) 