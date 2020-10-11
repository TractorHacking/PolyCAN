from transform import j1939

def test_rpm_parse():
    print("Testing RPM Parse...", end=' ')
    tests = [("F0 FF 7D 40 1F FF FF FF", 1000.0),
             ("F0 FF A7 80 3E FF FF FF", 2000.0),
             ("F0 FF 7D C0 5D FF FF FF", 3000.0)]
    passed = 0
    for input, output in tests:
        if int(j1939.convert_data(input, "4-5", "2 bytes")) * 0.125 == output:
            passed += 1
    if passed == 3:
        print("PASS (3/3)")
    else:
        print("FAIL (" + str(passed) + "/3)")

if __name__ == "__main__":
    test_rpm_parse()
