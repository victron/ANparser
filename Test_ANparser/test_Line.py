import unittest
import pickle
from os import linesep
# from ANparser import Line, LineRoot, LineCommand, LineEnd, SR
from ANconf import Section, SR, load, dump

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("__name__")

pairs_Line = [
    {"in": "service-construct service-rule NAT_RULE_ANY",
     "out": (SR, False, False, False)},
    {"in": " admin-state                                 enabled",
     "out": (SR, True, False, False)},
    # {"in": "  type            v-csm", "out": ""},
    {"in": " packet-filter PF_test_11001",
     "out": (SR, True, True, False)},
    {"in": " !",
     "out": (SR, True, True, False)},
    {"in": "!",
     "out": (SR, True, True, True)},

]

pair_text_SR = [
    {"in": 'test_file_1.txt',
     "out": (
         load, ['SR_mmkelwflaw_2020'], "SR_mmkelwflaw_2020", "enabled", "100", "2020", "HRG_msisdnffef3424", "all",
         "always-on", "disabled",
         ["PF__01", "PF__02", "PF__03",
          "PF__04", "PF__05"])},
    {"in":
         """service-construct service-rule SR_mmkelwflaw_2020
 admin-state                                 enabled
 priority                                    100
 service-data-flow-id                        2020
 http-rule-group                             HRG_msisdnffef3424
 tcp-filter                                  all
 service-activation                          always-on
 install-default-bearer-packet-filters-on-ue disabled
 packet-filter PF__01
 !
 packet-filter PF__02
 !
 packet-filter PF__03
 !
 packet-filter PF__04
 !
 packet-filter PF__05
 !
!""",
     "out": (
         load, ['SR_mmkelwflaw_2020'], "SR_mmkelwflaw_2020", "enabled", "100", "2020", "HRG_msisdnffef3424", "all",
     "always-on", "disabled",
         ["PF__01", "PF__02", "PF__03",
      "PF__04", "PF__05"])},
 ]


pair_text_SR_multiple = [
{"in": 'test_file_2.txt',
"out": 'test_file_2.pickle'},
]

pair_text_RG = [
{"in": 'test_RGs.txt', "out": 'test_RGs.pickle'},
]

pair_text_BP = [
{"in": 'test_BPs.txt', "out": 'test_BPs.pickle'},
]

class Test_1_Objects(unittest.TestCase):

    def test_1line_type(self):
        obj = Section()
        for i, pair in enumerate(pairs_Line):
            line = pair["in"]
            obj = obj.set_param(line)
            self.assertEqual(pair["out"][0], type(obj), f"error in parse method, line= {i}")
            self.assertEqual(pair["out"][1], hasattr(obj, "admin_state"), f"admin-state, line= {i}")
            self.assertEqual(pair["out"][2], hasattr(obj, "packet_filter"), f"packet-filter, line= {i}")
            self.assertEqual(pair["out"][3], obj.end, f"close flag, line= {i}")

    def test_2_Parser(self):
        for i, pair in enumerate(pair_text_SR):

            result = load(pair["in"])
            self.assertEqual(pair["out"][0], type(result), f"fail in pair num= {i}")
            self.assertEqual(pair["out"][1], list(result.sr.keys()), f"fail in pair num= {i}")
            self.assertEqual(pair["out"][2], result.sr['SR_mmkelwflaw_2020'].name, f"fail in pair num= {i}")
            self.assertEqual(pair["out"][3], result.sr['SR_mmkelwflaw_2020'].admin_state, f"fail in pair num= {i}")
            self.assertEqual(pair["out"][4], result.sr['SR_mmkelwflaw_2020'].priority, f"fail in pair num= {i}")
            self.assertEqual(pair["out"][5], result.sr['SR_mmkelwflaw_2020'].service_data_flow_id, f"fail in pair num= {i}")
            self.assertEqual(pair["out"][6], result.sr['SR_mmkelwflaw_2020'].http_rule_group, f"fail in pair num= {i}")
            self.assertEqual(pair["out"][7], result.sr['SR_mmkelwflaw_2020'].tcp_filter, f"fail in pair num= {i}")
            self.assertEqual(pair["out"][8], result.sr['SR_mmkelwflaw_2020'].service_activation, f"fail in pair num= {i}")
            self.assertEqual(pair["out"][9],
                             result.sr['SR_mmkelwflaw_2020'].install_default_bearer_packet_filters_on_ue, f"fail in pair num= {i}")
            self.assertEqual(pair["out"][10], result.sr['SR_mmkelwflaw_2020'].packet_filter, f"fail in pair num= {i}")
            # print(vars(result['SR_msisdn_add_2020']))
            # print("lllll", result['SR_msisdn_add_2020']["packet-filter"])

    def test_3_Parser_Multiple(self):
        for i, pair in enumerate(pair_text_SR_multiple):
            result = load(pair["in"])
            with open(pair["out"], 'rb') as f:
                result_etalon = pickle.load(f)
                # pickle.dump(result, f)
            for res in result_etalon.sr:
                self.assertEqual(result_etalon.sr[res].name, result.sr[res].name)
                for field in result_etalon.sr[res].allKeys:
                    try:
                        self.assertEqual(result_etalon.sr[res][field], result.sr[res][field])
                    except AttributeError:
                        pass

class Test_2_RGs(unittest.TestCase):
    def test_1_RG(self):
        for i, pair in enumerate(pair_text_RG):
            result = load(pair["in"])
            with open(pair["out"], "rb") as f:
                # pickle.dump(result, f)
                result_etalon = pickle.load(f)
            for res in result_etalon.rg:
                self.assertEqual(result_etalon.rg[res].name, result.rg[res].name)
                for field in result_etalon.rg[res].allKeys:
                    try:
                        self.assertEqual(result_etalon.rg[res][field], result.rg[res][field])
                    except AttributeError:
                        pass

    def test_2_BP(self):
        for i, pair in enumerate(pair_text_BP):
            result = load(pair["in"])
            with open(pair["out"], "rb") as f:
                # pickle.dump(result, f)
                result_etalon = pickle.load(f)
            for res in result_etalon.bp:
                # print("name=", result_etalon.bp[res].name, result.bp[res].name)
                self.assertEqual(result_etalon.bp[res].name, result.bp[res].name)
                for field in result_etalon.bp[res].allKeys:
                    try:
                        # print(f"field= {field} = ", result_etalon.bp[res][field], result.bp[res][field])
                        self.assertEqual(result_etalon.bp[res][field], result.bp[res][field])
                    except AttributeError:
                        pass

    def test_3_load_multiple_files(self):
        file_list = [pair_text_BP[0]["in"], pair_text_RG[0]["in"]]
        result = load(file_list)
        with open(pair_text_BP[0]["out"], "rb") as f:
            BPs_etalon = pickle.load(f)
        with open(pair_text_RG[0]["out"], "rb") as f:
            RGs_etalon = pickle.load(f)
        for res in BPs_etalon.bp:
            # print("name=", result_etalon.bp[res].name, result.bp[res].name)
            self.assertEqual(BPs_etalon.bp[res].name, result.bp[res].name)
            for field in BPs_etalon.bp[res].allKeys:
                try:
                    # print(f"field= {field} = ", result_etalon.bp[res][field], result.bp[res][field])
                    self.assertEqual(BPs_etalon.bp[res][field], result.bp[res][field])
                except AttributeError:
                    pass

        for res in RGs_etalon.rg:
            self.assertEqual(RGs_etalon.rg[res].name, result.rg[res].name)
            for field in RGs_etalon.rg[res].allKeys:
                try:
                    self.assertEqual(RGs_etalon.rg[res][field], result.rg[res][field])
                except AttributeError:
                    pass


# ########### private tests ############
# class Test_3_ALLs(unittest.TestCase):
#     def test_1_separated_files(self):
#         for i, file in enumerate(["private_BP_all.txt", "private_RG_all.txt", "private_SR_all.txt"]):
#             result = load(file)
#             print(vars(result))
#
#     def test_2_ALL(self):
#         for i, file in enumerate(["private_PARSE_ALL.txt"]):
#             result = load(file)
#             print(vars(result))
#
#


class Test_4_print(unittest.TestCase):
    def test_1_printOneObj(self):
        gen_object = load(pair_text_SR[1]["in"])
        result = str(dump(gen_object.sr["SR_mmkelwflaw_2020"]))
        self.assertEqual(pair_text_SR[1]["in"], result.replace(linesep, "\n"), "stdout not eq")
        dump(gen_object.sr["SR_mmkelwflaw_2020"], "temp.dump")
        with open("temp.dump", "r", newline=linesep) as f:
            result = f.read()
        self.assertEqual(pair_text_SR[1]["in"], result.replace(linesep, "\n"), "data in file not eq")

    def test_2_printMult(self):
        for i, pair in enumerate(pair_text_SR_multiple):
            gen_object = load(pair["in"])
            result = str(dump(gen_object.sr))
            with open(pair["in"], "r", newline=linesep) as etal:
                etalon = etal.read()
            self.assertEqual(etalon, result, "stdout not eq")

            dump(gen_object.sr, "temp.dump")
            with open("temp.dump", "r", newline=linesep) as dumpF:
                result = dumpF.read()
            self.assertEqual(etalon, result, "data in file not eq")

        for i, pair in enumerate(pair_text_RG):
            gen_object = load(pair["in"])
            result = str(dump(gen_object.rg))
            with open(pair["in"], "r", newline=linesep) as etal:
                etalon = etal.read()
            self.assertEqual(etalon, result, "stdout not eq")

            dump(gen_object.rg, "temp.dump")
            with open("temp.dump", "r", newline=linesep) as dumpF:
                result = dumpF.read()
            self.assertEqual(etalon, result, "data in file not eq")

    def test_3_printBP(self):
        for i, pair in enumerate(pair_text_BP):
            gen_object = load(pair["in"])
            result = str(dump(gen_object.bp))
            with open(pair["in"], "r", newline=linesep) as etal:
                etalon = etal.read()
            self.assertEqual(etalon, result, "stdout not eq")

            dump(gen_object.bp, "temp.dump")
            with open("temp.dump", "r", newline=linesep) as dumpF:
                result = dumpF.read()
            self.assertEqual(etalon, result, "data in file not eq")

########### private tests ############
class Test_5_ALLs(unittest.TestCase):
    def test_1_separated_files(self):
        for i, file in enumerate(["private_BP_all.txt",
                                  "private_RG_all.txt",
                                  "private_SR_all.txt"
                                  ]):
            gen_object = load(file)
            result = str(dump(gen_object))
            with open(file, "r", newline=linesep) as etal:
                etalon = etal.read()
            self.assertEqual(etalon, result, "stdout not eq")

            dump(gen_object, "temp.dump")
            with open("temp.dump", "r", newline=linesep) as dumpF:
                result = dumpF.read()
            self.assertEqual(etalon, result, "data in file not eq")

    def test_2_ALL(self):
        for i, file in enumerate(["private_PARSE_ALL.txt"]):
            result = load(file)
            gen_object = load(file)
            result = str(dump(gen_object))
            with open(file, "r", newline=linesep) as etal:
                etalon = etal.read()
            self.assertEqual(etalon, result, "stdout not eq")

            dump(gen_object, "temp.dump")
            with open("temp.dump", "r", newline=linesep) as dumpF:
                result = dumpF.read()
            self.assertEqual(etalon, result, "data in file not eq")