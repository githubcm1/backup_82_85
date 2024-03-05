from funcoes_nfc_pn7150 import PN7150
import funcoes_nfc

pn7150 = PN7150()

pn7150.when_tag_read = lambda text: [print(text), funcoes_nfc.grava_json(text)]

pn7150.start_reading()

pn7150.stop_reading()
