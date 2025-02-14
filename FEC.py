import reedsolo


def encode_reed_solomon(data: str, nsym=10):
    rs = reedsolo.RSCodec(nsym)  # Create a Reed-Solomon encoder with nsym redundancy symbols
    encoded_data = rs.encode(data.encode())
    return encoded_data


def decode_reed_solomon(encoded_data, nsym=10):
    rs = reedsolo.RSCodec(nsym)
    decoded_data = rs.decode(encoded_data)[0].decode()  # Extract the first element of the tuple
    return decoded_data


if __name__ == "__main__":
    # Input string
    data = "Hello World"
    print("Original Data:", data)

    # Encode the data
    encoded_data = encode_reed_solomon(data)
    print("Encoded Data:", encoded_data)

    # Introduce some errors (corrupt the data)
    corrupted_data = bytearray(encoded_data)
    corrupted_data[2] ^= 0xFF  # Flip some bits
    corrupted_data[5] ^= 0xFF
    corrupted_data = bytes(corrupted_data)
    print("Corrupted Data:", corrupted_data)

    # Decode the data
    try:
        decoded_data = decode_reed_solomon(corrupted_data)
        print("Decoded Data:", decoded_data)
    except reedsolo.ReedSolomonError as e:
        print("Decoding failed:", e)
