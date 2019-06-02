import unittest
import pickle
from os import linesep
from ANconf import Load, Dump, load, dump, show, SR, RG, BP
import copy

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("__name__")

pair_text = [
    {"in":
         """services charging billing-plan lklkdsmkm
 rating-group RadaskjfjkndX-CH
  fraud-charging false
 !
 rating-group RG_sferfe
  fraud-charging false
 !
 rating-group RG_aefeacecwa
  fraud-charging false
 !
!
""",
     "out": (
         Load, 1, 0,
         # "enabled", "100", "2020", "HRG_msisdnffef3424", "all",
     # "always-on", "disabled",
     #     ["PF__01", "PF__02", "PF__03",
     #  "PF__04", "PF__05"]
          )
     },
    {"in": """services charging billing-plan BP-ferfersr
 rating-group RG_rfawedawdea
  fraud-charging false
 !
 rating-group RG_wadwedewdaw
  fraud-charging false
 !
 rating-group RG_hawdawdADW
  fraud-charging false
 !
!
service-construct service-rule SR_dscdvsdvacacda
 admin-state                                 enabled
 priority                                    340
 service-data-flow-id                        9212
 http-rule-group                             HRG-cacdSCDdCC
 tcp-filter                                  all
 service-activation                          external-activation
 pcc-rule-name                               1030
 install-default-bearer-packet-filters-on-ue disabled
 packet-filter PF_05
 !
 packet-filter PF_06
 !
 packet-filter PF_07
 !
 packet-filter PF_08
 !
!
""",
     "out": (
         Load, 1, 1,
         # "enabled", "100", "2020", "HRG_msisdnffef3424", "all",
     # "always-on", "disabled",
     #     ["PF__01", "PF__02", "PF__03",
     #  "PF__04", "PF__05"]
          )
     }
 ]

pair_text_SR = [
    {"in": 'test_file_1.txt',
     "out": (
         Load, [str("SR_mmkelwflaw_2020")], "SR_mmkelwflaw_2020", "enabled", "100", "2020", "HRG_msisdnffef3424", "all",
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
         Load, ['SR_mmkelwflaw_2020'], "SR_mmkelwflaw_2020", "enabled", "100", "2020", "HRG_msisdnffef3424", "all",
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


class Test_1_Object(unittest.TestCase):

    def test_1_BP(self):
        for i, pair in enumerate(pair_text):
            obj = Load(pair["in"])
            self.assertTrue(isinstance(obj, Load), f"wrong object")
            print(obj.config["services charging billing-plan"])
            self.assertEqual(pair["out"][1], len(obj.config["services charging billing-plan"]), f"obj num, line= {i}")
            if i == 0:
                with self.assertRaises(KeyError) as cm1:
                    self.assertEqual(pair["out"][2], len(obj.config["service-construct service-rule"]), f"line= {i}")
                self.assertTrue("service-construct service-rule" in str(cm1.exception),
                                "waiting exeption, when trying to GET not existen (not created) key")
            if i == 1:
                # same as above, but now key present
                self.assertEqual(pair["out"][2], len(obj.config["service-construct service-rule"]), f"line= {i}")
            # self.assertEqual(pair["out"][3], obj.end, f"close flag, line= {i}")
            # print(Dump(obj.config["services charging billing-plan"][0]))


    def test_2_Parser(self):
        for i, pair in enumerate(pair_text_SR):

            result = Load(pair["in"])
            sr = result.config["service-construct service-rule"]
            sr_dic = {i.name: i for i in sr}
            self.assertEqual(pair["out"][0], type(result), f"fail in pair num= {i}")
            self.assertEqual(pair["out"][1], [str(sr[0]),], f"fail in pair num= {i}")
            self.assertEqual(pair["out"][2], sr_dic['SR_mmkelwflaw_2020'].name, f"fail in pair num= {i}")
            self.assertEqual(pair["out"][3], sr_dic['SR_mmkelwflaw_2020']["admin-state"], f"fail in pair num= {i}")
            self.assertEqual(pair["out"][4], sr_dic['SR_mmkelwflaw_2020']["priority"], f"fail in pair num= {i}")
            self.assertEqual(pair["out"][5], sr_dic['SR_mmkelwflaw_2020']["service-data-flow-id"], f"fail in pair num= {i}")
            self.assertEqual(pair["out"][6], sr_dic['SR_mmkelwflaw_2020']["http-rule-group"], f"fail in pair num= {i}")
            self.assertEqual(pair["out"][7], sr_dic['SR_mmkelwflaw_2020']["tcp-filter"], f"fail in pair num= {i}")
            self.assertEqual(pair["out"][8], sr_dic['SR_mmkelwflaw_2020']["service-activation"], f"fail in pair num= {i}")
            self.assertEqual(pair["out"][9],
                             sr_dic['SR_mmkelwflaw_2020']["install-default-bearer-packet-filters-on-ue"], f"fail in pair num= {i}")
            self.assertEqual(pair["out"][10], sr_dic['SR_mmkelwflaw_2020']["packet-filter"], f"fail in pair num= {i}")
            # d = Dump(sr_dic['SR_mmkelwflaw_2020'])
            # print(d)

    def test_3_Parser_Multiple(self):
        for i, pair in enumerate(pair_text_SR_multiple):
            result = Load(pair["in"])
            with open(pair["out"], 'rb') as f:
                result_etalon = pickle.load(f)
                # pickle.dump(result, f, protocol=0)
            for res in result_etalon.config["service-construct service-rule"]:
                sr = result.config["service-construct service-rule"]
                sr_dic = {i.name: i for i in sr}
                self.assertEqual(res.name, sr_dic[res.name].name)
                for field in res:
                    try:
                        self.assertEqual(res[field], sr_dic[res.name][field])
                    except AttributeError:
                        pass


class Test_2_RGs(unittest.TestCase):
    def test_1_RG(self):
        for i, pair in enumerate(pair_text_RG):
            result = load(pair["in"])
            with open(pair["out"], "rb") as f:
                # pickle.dump(result, f, 0)
                result_etalon = pickle.load(f)
            for res in result_etalon.config["services charging rating-group"]:
                rg = result.config["services charging rating-group"]
                rg_dic = {i.name: i for i in rg}
                self.assertEqual(res.name, rg_dic[res.name].name)
                for field in res:
                    try:
                        self.assertEqual(res[field], rg_dic[res.name][field])
                    except AttributeError:
                        pass

    def test_2_BP(self):
        for i, pair in enumerate(pair_text_BP):
            result = load(pair["in"])
            with open(pair["out"], "rb") as f:
                # pickle.dump(result, f, 0)
                result_etalon = pickle.load(f)
            for res in result_etalon.config["services charging billing-plan"]:
                bp = result.config["services charging billing-plan"]
                bp_dic = {i.name: i for i in bp}
                # print("name=", result_etalon.bp[res].name, bp_dic[res].name)
                self.assertEqual(res.name, bp_dic[res.name].name)
                for field in res:
                    try:
                        # print(f"field= {field} = ", result_etalon.bp[res][field], [rg.name for rg in bp_dic[res][field]])
                        self.assertEqual([rg.name for rg in res[field]], [rg.name for rg in bp_dic[res.name][field]])
                    except AttributeError:
                        pass

    def test_3_load_multiple_files(self):
        file_list = [pair_text_BP[0]["in"], pair_text_RG[0]["in"]]
        result = load(file_list)
        with open(pair_text_BP[0]["out"], "rb") as f:
            BPs_etalon = pickle.load(f)
        with open(pair_text_RG[0]["out"], "rb") as f:
            # pickle.dump(result, f)
            RGs_etalon = pickle.load(f)
        result.config["services charging billing-plan"]
        for etal, res in zip(BPs_etalon.config["services charging billing-plan"],
                       result.config["services charging billing-plan"]):
            self.assertEqual(etal.name, res.name)
            for etal_field, res_field in zip(etal["rating-group"], res["rating-group"]):
                # try:
                # print(f"field= {etal_field} = ", etal_field["fraud-charging"], res_field.name)
                self.assertEqual(etal_field.name, res_field.name, "check name of RG")
                self.assertEqual(etal_field["fraud-charging"], res_field["fraud-charging"],
                                 "check fraud-charging subfield")
                # except AttributeError:
                #     pass

        for etal, res in zip(RGs_etalon.config["services charging rating-group"],
                             result.config["services charging rating-group"]):
            self.assertEqual(etal.name, res.name)
            for etal_field, res_field in zip(etal.items(), res.items()):
                self.assertEqual(etal_field, res_field, "tuple(key, value)")
                # print(f"field= {etal_field} = ", etal_field, res_field)
            for sr_etal, sr_res in zip(etal["service-rule"], res["service-rule"]):
                self.assertEqual(sr_etal, sr_res, "values of service-rule")
                # print(sr_etal, sr_res)


class Test_4_print(unittest.TestCase):
    def test_1_printOneObj(self):
        gen_object = load(pair_text_SR[1]["in"])
        result = str(dump(gen_object.config["service-construct service-rule"][0]))
        self.assertEqual(pair_text_SR[1]["in"], result.replace(linesep, "\n"), "stdout not eq")
        dump(gen_object.config["service-construct service-rule"][0], "temp.dump")
        with open("temp.dump", "r", newline=linesep) as f:
            result = f.read()
        self.assertEqual(pair_text_SR[1]["in"], result.replace(linesep, "\n"), "data in file not eq")

    def test_2_printMult(self):
        for i, pair in enumerate(pair_text_SR_multiple):
            gen_object = load(pair["in"])
            result = str(dump(gen_object.config["service-construct service-rule"]))
            with open(pair["in"], "r", newline=linesep) as etal:
                etalon = etal.read()
            self.assertEqual(etalon, result, "stdout not eq")

            dump(gen_object.config["service-construct service-rule"], "temp.dump")
            with open("temp.dump", "r", newline=linesep) as dumpF:
                result = dumpF.read()
            self.assertEqual(etalon, result, "data in file not eq")

        for i, pair in enumerate(pair_text_RG):
            gen_object = load(pair["in"])
            result = str(dump(gen_object.config["services charging rating-group"]))
            with open(pair["in"], "r", newline=linesep) as etal:
                etalon = etal.read()
            self.assertEqual(etalon, result, "stdout not eq")

            dump(gen_object.config["services charging rating-group"], "temp.dump")
            with open("temp.dump", "r", newline=linesep) as dumpF:
                result = dumpF.read()
            self.assertEqual(etalon, result, "data in file not eq")

    def test_3_printBP(self):
        for i, pair in enumerate(pair_text_BP):
            gen_object = load(pair["in"])
            result = str(dump(gen_object.config["services charging billing-plan"]))
            with open(pair["in"], "r", newline=linesep) as etal:
                etalon = etal.read()
            self.assertEqual(etalon, result, "stdout not eq")

            dump(gen_object.config["services charging billing-plan"], "temp.dump")
            with open("temp.dump", "r", newline=linesep) as dumpF:
                result = dumpF.read()
            self.assertEqual(etalon, result, "data in file not eq")

class Test_6_Create_Objects(unittest.TestCase):
    def test_1_create_RG(self):
        test_obj = SR("kjfsaljeowiqjiwndnwan")
        test_obj["admin-state"] = "enabled"
        test_obj["priority"] = "100"

        with self.assertRaises(KeyError) as cm:
            test_obj["failString"] = "test-wrong-string"
        self.assertTrue("failString" in str(cm.exception), "waiting exeption, when trying to SET wrong key")

        test_obj.failString_A = "failString_A"      # TODO: at that moment it's allowed
        test_obj["service-data-flow-id"] = "1111"
        test_obj["tcp-filter"] = "yes"
        test_obj["service-activation"] = "always-on"
        test_obj["install-default-bearer-packet-filters-on-ue"] = "m"

        self.assertEqual("kjfsaljeowiqjiwndnwan", test_obj.name)
        self.assertEqual("failString_A", test_obj.failString_A, "python allowing sett custom attributes")
        self.assertEqual("enabled", test_obj["admin-state"])
        self.assertEqual("100", test_obj["priority"])
        self.assertEqual("1111", test_obj["service-data-flow-id"])
        self.assertEqual("yes", test_obj["tcp-filter"])
        self.assertEqual("always-on", test_obj["service-activation"])
        self.assertEqual("m", test_obj["install-default-bearer-packet-filters-on-ue"])
        with self.assertRaises(KeyError) as cm1:
            failString = test_obj["failString"]
        self.assertTrue("failString" in str(cm1.exception), "waiting exeption, when trying to GET wrong key")


    def test_2_create_SR(self):
        # create SR with parameters in random order
        test_obj = SR("SR_test-1010")
        test_obj["admin-state"] = "enabled"
        test_obj["priority"] = "320"
        test_obj["service-data-flow-id"] = "1011"
        test_obj["http-rule-group"] = "HRG-test_1011"
        test_obj["tcp-filter"] = "all"
        test_obj["service-activation"] = "external-activation"
        test_obj["install-default-bearer-packet-filters-on-ue"] = "disabled" # wrong order with next line
        test_obj["pcc-rule-name"] = "1010"
        test_obj["packet-filter"] = ["PF_test_01", "PF_test_02", "PF_test_03", "PF_test_04"]

        test_obj_dump = show(test_obj).output
        with open("test_parm_order.txt", "r", newline=linesep) as f:
            etalon = f.read()

        self.assertEqual(etalon, test_obj_dump, "parameters in wrong order")

# ########### private tests ############
# class Test_100_print(unittest.TestCase):
#     # compare manualy output
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


########### private tests ############
# class Test_100_ALLs(unittest.TestCase):
#     # load into objects,  then dump and compare files
#     def test_1_separated_files(self):
#         for i, file in enumerate(["private_BP_all.txt",
#                                   "private_RG_all.txt",
#                                   "private_SR_all.txt"
#                                   ]):
#             gen_object = load(file)
#             result = str(dump(gen_object))
#             with open(file, "r", newline=linesep) as etal:
#                 etalon = etal.read()
#             self.assertEqual(etalon, result, "stdout not eq")
#
#             dump(gen_object, "temp.dump")
#             with open("temp.dump", "r", newline=linesep) as dumpF:
#                 result = dumpF.read()
#             self.assertEqual(etalon, result, "data in file not eq")
#
#     def test_2_ALL(self):
#         for i, file in enumerate(["private_PARSE_ALL.txt"]):
#             result = load(file)
#             gen_object = load(file)
#             result = str(dump(gen_object))
#             with open(file, "r", newline=linesep) as etal:
#                 etalon = etal.read()
#             self.assertEqual(etalon, result, "stdout not eq")
#
#             dump(gen_object, "temp.dump")
#             with open("temp.dump", "r", newline=linesep) as dumpF:
#                 result = dumpF.read()
#             self.assertEqual(etalon, result, "data in file not eq")