# Visualization app in python for IBH Link S7++
Project is port to python and develop of simple "linux shell" app, provided by "IBHsoftec GmbH" with drivers for this gateway.
For details of "Ibh link" API look in [IBH Link S7++](https://www.ibhsoftec.com/IBH-Link-S7-PP-Eng) download section.

![Ibh link s7 ++ img](https://www.ibhsoftec.com/WebRoot/Store6/Shops/63444704/4F32/97CB/C3A1/E005/5406/C0A8/2981/4069/20266_ml.gif)

## Road map
I plan to equip app in following functionalities:
* Support API reads & writes Bits, Bytes, Words, Double Words, Byte fields from areas: M, I/E, Q/A, DB
* Cyclic operation of above reads & writes
* Standard GUI for presentation of visualization screens writen in PyQT
* Loading qt-designer *.ui files with screens and parse widgets properties 'What's this' for desired PLC variables to refresh