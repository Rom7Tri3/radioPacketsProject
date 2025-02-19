import reedsolo

def encode_reed_solomon(data: str, nsym=15) -> bytes:
    """Encodes a string using Reed-Solomon error correction."""
    rs = reedsolo.RSCodec(nsym)
    return rs.encode(data.encode())

def decode_reed_solomon(encoded_data: bytes, nsym=15) -> str:
    """Decodes a Reed-Solomon encoded byte sequence."""
    rs = reedsolo.RSCodec(nsym)
    decoded_bytes = rs.decode(encoded_data)
    return decoded_bytes.decode() if isinstance(decoded_bytes, bytes) else decoded_bytes[0].decode()

def binary_array_to_bytes(binary_array) -> bytes:
    """Converts a binary array to a bytes object."""
    binary_string = ''.join(map(str, binary_array))
    return bytes(int(binary_string[i:i + 8], 2) for i in range(0, len(binary_string), 8))

def corrupt_data(encoded_data: bytes, error_positions: list) -> bytes:
    """Introduces bit errors at specified positions in a byte sequence."""
    corrupted_data = bytearray(encoded_data)
    for pos in error_positions:
        corrupted_data[pos] ^= 0xFF  # Flip bits at the specified positions
    return bytes(corrupted_data)

if __name__ == "__main__":
    data = "Hello World"
    print("Original Data:", data)

    encoded_data = encode_reed_solomon(data)
    print("Encoded Data:", encoded_data)

    corrupted_data = corrupt_data(encoded_data, [2, 5])
    print("Corrupted Data:", corrupted_data)

    try:
        decoded_data = decode_reed_solomon(corrupted_data)
        print("Decoded Data:", decoded_data)
    except reedsolo.ReedSolomonError as e:
        print("Decoding failed:", e)
