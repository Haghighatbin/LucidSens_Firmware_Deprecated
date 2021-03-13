import machine
ow = machine.Onewire(4)

# ow.deinit()
# ow.scan(False) # returns a hex string
# if True returns family code, serial number and crc
# ow.search() does the same as scan
# ow.rom_code(0) # returns ROM code, same value as above family no.
# ow.reset() # resets 1-wire
# ow.readbyte() # reads 1 byte from the 1-wire dev
# ow.writebyte(val) # writes to 1-wire
# ow.readbytes(len) # returns string
# ow.writebytes(len) # writes multiple string or bytearray

# ds0 = machine.Onewire.ds18x20(ow, dev)
ds0 = machine.Onewire.ds18x20(ow, 0)
ds0.deinit() # Note: Onewire object can be deinitialized only if all ds18x20 object using it are deinitialized.
ds0.read_temp() # returns the last (float) value read from ds-dev
# ds0.read_tempinit() # returns the last (raw) value read from ds-dev
ds0.convert_read() # starts actual reading returns float in Celcius
# ds.convert() # returns temp from all attached devs
# ds.get_pwrmode()
# Return device power mode:
# 0 device operates in parasite power mode
# 255 device operates in normal power mode
# 2 device not responding
# 3 error
# ds.rom_code() # returns ROM code in hex string
# ds.get_res() and ds.set_res(res) # getting and setting resolution 12bit default


