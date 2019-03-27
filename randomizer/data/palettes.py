# Data module for palette data.

from randomizer.logic import utils
from randomizer.logic.patch import Patch

class Palette:
    
    #Address array = should be an array containing all child arrays that need palette changes
    #Child arrays should be 16 addresses in length... or maybe 15. Seems the first address is unused?
    starting_addresses = []
    doll_addresses = [] # only populate this if it follows different palette rules. currently only used for mario
    poison_addresses = []
    underwater_addresses = []
    
    colours = []
    poison_colours = []
    underwater_colours = []
    name_address = 0
    clone_name_address = 0
    name = ""
    rename_character = True
        
    #TODO poison palettes, underwater palettes
    
class MarioPalette(Palette):
    starting_addresses = [
        #overworld
        0x257998,
        #battle
        0x257B78,
        #portrait
        0x256B88,
        #doll 2
        0x257A4C,
        #scarecrow/mushroom
        0x256AF2
        
    ]
    doll_addresses = [
        #doll 1 - for mario, 6th colour should be 7th in palette, 7th colour should be 8th in palette, and 8th and 9th colour should both be 9th in palette. 10th colour should be 11th in palette, 11th and 12th colour should be 12th in palette
        0x2576E6
    ]
    poison_addresses = [0x2579D4, 0x257BB4]
    #Poison palette for battle portrait will not be edited. It is shared by all 5 characters.
    underwater_addresses = [0x257A10, 0x257BF0]
    name_address = 0x3A134D
    clone_name_address = 0x399A96
    #poison - 646
    #underwater - 648
    name = "Mario"
    
    
class MallowPalette(Palette):
    starting_addresses = [
        #overworld
        0x2581AE,
        #battle
        0x258244,
        #portrait
        0x256B4C,
        #doll 1 - for mallow, skip 8th and 9th colour replacement
        #maybe leave this out since mario and peach in credits have to share a palette and im probably not going to change them
        #0x2583CA,
        #scarecrow/mushroom
        0x256B4C
    ]
    poison_addresses = [0x2581EA, 0x258280]
    #Poison palette for battle portrait will not be edited. It is shared by all 5 characters.
    underwater_addresses = [0x258226, 0x2582BC]
    name_address = 0x3A1375
    clone_name_address = 0x399ACA
    #poison - 704
    #underwater - 706
    name = "Mallow"
     
class GenoPalette(Palette):
    starting_addresses = [
        #overworld
        0x258046,
        #battle
        0x2580FA,
        #portrait
        0x256B6A,
        #doll 1
        0x257A88,
        #scarecrow/mushroom
        0x256B6A
    ]
    poison_addresses = [0x258082, 0x258136]
    #Poison palette for battle portrait will not be edited. It is shared by all 5 characters.
    underwater_addresses = [0x2580BE, 0x258172]
    name_address = 0x3A136B
    clone_name_address = 0x399ABD
    #poison - 693
    #underwater - 695
    name = "Geno"
    
class BowserPalette(Palette):
    starting_addresses = [
        #overworld
        0x257DD0,
        #battle
        0x257E66,
        #portrait
        0x256B2E,
        #doll 1
        0x257AA6,
        #scarecrow/mushroom
        0x256B2E
    ]
    name_address = 0x3A1361
    clone_name_address = 0x399AB0
    poison_addresses = [0x257E0C, 0x257EA2]
    #Poison palette for battle portrait will not be edited. It is shared by all 5 characters.
    underwater_addresses = [0x257E48, 0x257EDE]
    #poison - 671
    #underwater - 673
    name = "Bowser"
    
class ToadstoolPalette(Palette):
    starting_addresses = [
        #overworld
        0x257CA4,
        #battle
        0x257D3A,
        #portrait
        0x256B10,
        #doll 1
        0x257AC4,
        #scarecrow/mushroom
        0x256B10
    ]
    name_address = 0x3A1357
    clone_name_address = 0x399AA3
    poison_addresses = [0x257CE0, 0x257D76]
    #Poison palette for battle portrait will not be edited. It is shared by all 5 characters.
    underwater_addresses = [0x257D1C, 0x257DB2]
    #poison - 656
    #underwater - 658
    name = "Toadstool"
    
    
#mario palettes
class MarioJumpman(MarioPalette):
    colours = ["F8F8F8", "F8C880", "C08848", "A86848", "783830", "3838E0", "0000D8", "101090", "600000", "B83838", "A00000", "581818", "D8D8E0", "888898", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Jumpman"
class MarioFireMario(MarioPalette):
    colours = ["F8F8F8", "F8D0A0", "C09868", "A87858", "785030", "F0F0F0", "D0D0D0", "989898 ", "484848", "D03838", "A00000", "680000", "E0D8D8", "988888", "181818"]
    poison_colours = ["F8C0F8", "F898F8", "D870C0", "C058A0", "883050", "F8B0F8", "E898F8", "A870F8", "503080", "E82060", "B00000", "700000", "F8A0F8", "A860F8", "181020"]
    underwater_colours = ["7C7CAD", "7C6881", "604C65", "543C5E", "3C284A", "7878A9", "686899", "4C4C7D", "242456", "681C4E", "500032", "340032", "706C9D", "4C4475", "0C0C3E"]
    name = "Fire Mario"
class MarioLuigi(MarioPalette):
    colours = ["F8F8F8", "F8C880", "C08848", "A86848", "382810", "28A020", "187818", "207020", "100800", "3838E0", "0000D8", "000060", "E0D8D8", "988888", "101808"]
    poison_colours = ["F8B8F8", "F89880", "F86848", "F85048", "701810", "507820", "305818", "405020", "200000", "7028E0", "0000D8", "000060", "F8A0D8", "F86888", "101808"]
    underwater_colours = ["7c7cad", "7c6471", "604456", "543456", "1c143a", "145042", "0c3c3e", "103842", "080432", "1c1ca1", "00009d", "000062", "706c9d", "4c4475", "080c36"]
    name = "Luigi"
class MarioFireLuigi(MarioPalette):
    colours = ["F8F8F8", "F8C880", "C08848", "A86848", "783830", "F8F8F8", "E8E8E8", "B8B8B8", "600000", "389830", "388838", "207820", "D8D8D8", "988888", "181818"]
    name = "Fire Luigi"
class MarioWario(MarioPalette):
    colours = ["F8F8F8", "F0B8A8", "C08870", "A86860", "783830", "F8D848", "D0B020", "A88010", "604800", "9038B0", "780090", "480060", "F0E8D8", "989078", "181818"]
    poison_colours = ["F8C0F8", "F888F8", "D860C8", "C048A8", "882050", "F8A080", "E88830", "C06018", "683000", "A020F8", "8800F8", "5000A8", "F8A8F8", "A868D8", "181020"]
    underwater_colours = ["7C7CAD", "785C85", "604469", "543462", "3C1C4A", "7C6C56", "685842", "54403A", "302432", "481C89", "3C0079", "240062", "78749D", "4C486D", "0C0C3E"]
    name = "Wario"
class MarioWaluigi(MarioPalette):
    colours = ["F8F8F8", "F8D090", "C89058", "B07058", "783830", "9040E0", "6818C0", "380888", "100060", "505050", "383840", "000000", "E0D8D8", "988888", "181818"]
    poison_colours = ["F8A8F8", "F888E8", "C86090", "B04890", "782048", "9028F8", "6810F8", "6810F8", "100098", "503080", "382068", "000000", "E090F8", "9858D8", "181020"]
    underwater_colours = ["7C7CAD", "7C6879", "64485E", "58385E", "3C1C4A", "4820A1", "340C91", "340C91", "080060", "28285A", "1C1C52", "000032", "706C9D", "4C4475", "0C0C3E"]
    name = "Waluigi"
class MarioBuilder(MarioPalette):
    colours = ["F8F8F8", "F8C880", "C08848", "A86848", "783830", "C89030", "B07820", "A06820", "885820", "C85038", "984030", "702820", "E0D8D8", "988888", "201010"]
    poison_colours = ["F8F8F8", "F0A8B8", "B86880", "A05878", "703850", "B86078", "A85068", "A04860", "804050", "C04880", "903860", "682848", "E0D8D8", "988890", "201018"]
    underwater_colours = ["7878B0", "786070", "604058", "503058", "381848", "604848", "583840", "503040", "402840", "602850", "482048", "381040", "7068A0", "484078", "100838"]
    name = "Builder"
class MarioMegaman(MarioPalette):
    colours = ["F8F8F8", "F8C880", "C08848", "A86848", "783830", "18A0F8", "1018F8", "0018E0", "000088", "3838E0", "0000D8", "000060", "E0D8D8", "988888", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Megaman"
class MarioGrey(MarioPalette):
    colours = ["F8F8F8", "F8C880", "C08848", "A86848", "783830", "18A0F8", "1018F8", "0018E0", "000088", "3838E0", "0000D8", "000060", "E0D8D8", "988888", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Grey"
    rename_character = False
class MarioZombie(MarioPalette):
    colours = ["E8E0B8", "98A860", "607048", "484828", "383830", "A88050", "886848", "704000", "602000", "781818", "600000", "200000", "E0D8D8", "988888", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Zombie"
    rename_character = False
class MarioSponge(MarioPalette):
    colours = ["F8F8F8", "F8C8A0", "C09868", "A86848", "785848", "E88038", "C06000", "984800", "600000", "505050", "303030", "000000", "E0D8D8", "988888", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Sponge"
class MarioPretzel(MarioPalette):
    colours = ["F8F8F8", "F8E0C8", "B8A898", "A88078", "785848", "905818", "703800", "402000", "300000", "505050", "303030", "000000", "E0D8D8", "988888", "181818"]
    name = "Pretzel"
class MarioMarlon(MarioPalette):
    colours = ["F8F8F8", "A06830", "805818", "684018", "402000", "C03098", "A03068", "701048", "480020", "404058", "303048", "202038", "E0D8D8", "988888", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Marlon"
#mallow palettes
class MallowMokura(MallowPalette):
    colours = ["E0F878", "90F090", "78D878", "58A058", "283828", "606060", "404040", "202020", "300810", "80A080", "507050", "204020", "608860", "486848", "181818"]
    poison_colours = ["F8C0D8", "A0B0F8", "88A0D8", "6070A0", "282048", "6848A8", "482870", "201030", "300018", "9070E8", "585090", "202830", "6860A8", "504880", "181020"]
    underwater_colours = ["707C6D", "487879", "3C6C6D", "2C505E", "141C46", "303062", "202052", "101042", "18043A", "405071", "28385A", "102042", "304462", "243456", "0C0C3E"]
    name = "Mokura"
class MallowFrog(MallowPalette):
    colours = ["50C800", "50A800", "188800", "004800", "004000", "C02068", "902848", "003800", "001800", "003800", "001000", "002800", "006000", "006800", "000000"]
    poison_colours = ["608800", "606800", "005000", "002000", "001800", "F80060", "C00038", "001000", "000000", "001000", "000000", "000000", "003000", "003000", "000000"]
    underwater_colours = ["2E6A1E", "2E5A1E", "124A1E", "052A1E", "05261E", "661652", "4E1A42", "05221E", "05121E", "05221E", "050E1E", "051A1E", "05361E", "053A1E", "05051E"]
    name = "Frog"
class MallowPalom(MallowPalette):
    colours = ["f0e5d9", "f0d7bf", "efbd8c", "c7905a", "403828", "ce3939", "ad1010", "422110", "30170a", "78b820", "6b8c21", "526318", "a17f5d", "8F663F", "400808"]
    poison_colours = ["F8F8F8", "F8E8F8", "F8C8F8", "D090B8", "302840", "D82868", "B80008", "300808", "200000", "70C030", "609030", "405820", "A080C8", "906080", "300000"]
    underwater_colours = ["78749d", "786c91", "786079", "64485e", "201c46", "681c4e", "58083a", "20103a", "180c36", "3c5c42", "344842", "28303e", "504062", "483452", "200436"]
    name = "Palom"
class MallowPorom(MallowPalette):
    colours = ["f0e5d9", "f0d7bf", "efbd8c", "c7905a", "403828", "6B8C21", "526318", "422110", "30170a", "CE3939", "AD1010", "750B0B", "a17f5d", "8F663F", "281800"]
    poison_colours = ["F8F8F8", "F8E8F8", "F8C8F8", "D090B8", "302840", "609030", "405820", "300808", "200000", "D82868", "B80008", "750b6c", "A080C8", "906080", "300000"]
    underwater_colours = ["78749d", "786c91", "786079", "64485e", "201c46", "344842", "28303e", "20103a", "180c36", "681c4e", "58083a", "3a0537", "504062", "483452", "200436"]
    name = "Porom"
class MallowCloud(MallowPalette):
    colours = []
    poison_colours = []
    underwater_colours = []
    name = "Cloud"
    rename_character = False
class MallowStormy(MallowPalette):
    colours = ["E8E8F8", "C8C8D8", "B8B8C8", "808090", "484858", "8060C8", "502868", "302078", "101050", "E0E840", "C8A818", "605030", "8088C8", "686888", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Stormy"
    rename_character = False
class MallowLight(MallowPalette):
    colours = ["F8F8F8", "F0F0F0", "D8D8D8", "A0A0A0", "404040", "B8A0F8", "6860F8", "464050", "101010", "76ABEE", "4480CA", "3B5678", "8888A0", "686868", "181818"]
    poison_colours = ["F8F8A0", "F8F898", "E0E888", "A8B068", "404028", "C0B0A0", "6868A0", "484030", "101008", "78B898", "408880", "386048", "889068", "687040", "181810"]
    underwater_colours = ["7c7cad", "7878a9", "6c6c9d", "505081", "202052", "5c50ad", "3430ad", "24205a", "08083a", "3c54a9", "204095", "1c2c6d", "444481", "343465", "0c0c3e"]
    name = "Light"
    rename_character = False
class MallowWater(MallowPalette):
    colours = ["F8F8F8", "70D0E0", "58B8C8", "388090", "105878", "6868D0", "282848", "382038", "100810", "E8E8F8", "6868D0", "282848", "388090", "186070", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Water"
    rename_character = False
class MallowRed(MallowPalette):
    colours = ["F8F0F8", "F0D0E0", "E0A0D8", "A07088", "403828", "D83030", "902828", "582038", "301010", "804040", "582020", "180000", "D08080", "684888", "181818"]
    poison_colours = ["F8B0F8", "F898F8", "F870F8", "B050F8", "482048", "F82050", "A01848", "601060", "300018", "902870", "601030", "180000", "E860E8", "7030F8", "181020"]
    underwater_colours = ["7C78AD", "7868A1", "70509D", "503875", "201C46", "6C184A", "481446", "2C104E", "18083A", "402052", "2C1042", "0C0032", "684071", "342475", "0C0C3E"]
    name = "Red"
    rename_character = False
class MallowMint(MallowPalette):
    colours = ["F0F8F0", "E8F0E8", "C0E8B8", "A0C888", "506850", "70B878", "40B850", "202858", "080830", "0070A8", "005080", "003860", "98D8A0", "506848", "181818"]
    poison_colours = ["F0F0F0", "E8F0E8", "D0D0D0", "B0A8A8", "586058", "909098", "708080", "382858", "180830", "4838A8", "382880", "282060", "B0B8B8", "585858", "181818"]
    underwater_colours = ["7878A8", "7078A8", "607090", "506078", "283058", "385870", "205858", "101060", "000048", "003888", "002870", "001860", "486880", "283058", "080840"]
    name = "Mint"
    rename_character = False
class MallowDemon(MallowPalette):
    colours = ["403038", "283030", "282028", "201018", "182018", "081010", "182020", "182020", "300810", "000000", "100000", "101810", "181810", "181818", "F81818"]
    poison_colours = []
    underwater_colours = []
    name = "Demon"
    rename_character = False
#geno palettes
class GenoPink(GenoPalette):
    colours = ["F8F8F8", "F8E8B0", "E09870", "985010", "502818", "F898F8", "E848B0", "B02080", "700000", "F8D038", "F88820", "603000", "D0C8C8", "786860", "181818"]
    poison_colours = ["F8F8F8", "F8E8B0", "A8A8D8", "986030", "502828", "F8A8F8", "A878C8", "704890", "581820", "E0D028", "B0A018", "603000", "C8C8C8", "888888", "181818"]
    underwater_colours = ["B0B0D0", "B0A8A0", "A07070", "704030", "402828", "B050D0", "A830A0", "802080", "581028", "B09850", "B06840", "301832", "9890B0", "605068", "181818"]
    name = "Millnium"
class GenoMagikoopa(GenoPalette):
    colours = ["F8F8F8", "F0D860", "F8B000", "B06028", "481000", "3008F8", "1800B0", "080068", "300040", "007800", "F8F800", "602000", "000000", "686070", "181818"]
    poison_colours = ["F8F8F8", "E0A0A8", "E05878", "A84868", "400820", "8008F8", "5800B0", "300068", "300040", "304038", "E08078", "581030", "000000", "686070", "181818"]
    underwater_colours = ["7878B0", "786860", "785830", "583048", "200830", "180050", "080088", "000068", "180050", "003830", "787830", "301030", "000030", "303068", "080840"]
    name = "Magikoopa"
class GenoMagikoopaRed(GenoPalette):
    colours = ["F8F8F8", "F0D860", "C08030", "804818", "402810", "B80000", "A80000", "880000", "800000", "F8C000", "F85000", "682018", "B0A090", "686070", "181818"]
    poison_colours = ["A8F8F8", "A0E070", "808028", "503800", "181800", "700000", "680000", "500000", "500000", "A8C800", "A84800", "301000", "70A0C0", "305890", "000000"]
    underwater_colours = ["7C7CAD", "786C61", "604049", "40243D", "201439", "5C0031", "540031", "440031", "400031", "7C6031", "7C2831", "341C3D", "585079", "343069", "0C0C3D"]
    name = "Magikoopa"
class GenoLink(GenoPalette):
    colours = ["F8F8F8", "f0a068", "b86820", "8E3D3D", "402810", "78B820", "509010", "38650B", "274707", "f87800", "E860B0", "682018", "B0A090", "686070", "181818"]
    poison_colours = ["F8C0F8", "F870D0", "C84828", "902070", "300000", "708828", "486000", "284800", "182000", "F85000", "F838F8", "600018", "C070F8", "6038E0", "000018"]
    underwater_colours = ["7c7cad", "785065", "5c3442", "482052", "20143a", "3c5c42", "28483a", "1c3436", "142436", "7c3c32", "743089", "34103e", "585079", "343069", "0c0c3e"]
    name = "Zelda"
class GenoVlados(GenoPalette):
    colours = ["F8E0E0", "B0B0B0", "808080", "606060", "202018", "B01818", "800000", "680000", "200000", "D0C8D0", "D0C8D0", "383838", "B0A090", "686868", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Vlados"
class GenoLight(GenoPalette):
    colours = ["F8F8F8", "F0D8D8", "C08030", "804818", "402810", "00C0C0", "009090", "007070", "004848", "F8C0C0", "F85050", "682020", "A06838", "686060", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Light"
    rename_character = False
class GenoPurple(GenoPalette):
    colours = ["F8F8F8", "F8E8B0", "E09870", "985010", "502818", "A848F8", "8828D8", "6818B8", "481878", "C08870", "F87800", "603000", "908888", "686060", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Purple"
    rename_character = False
class GenoGrey(GenoPalette):
    colours = []
    poison_colours = []
    underwater_colours = []
    name = "Grey"
    rename_character = False
#bowser palettes
class BowserDrybone(BowserPalette):
    colours = ["F8F0F0", "E8E0B0", "F0E8C0", "B81010", "501818", "383030", "202020", "181010", "201818", "C8B8A0", "988870", "200808", "908080", "604040", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Dry Bone"
class BowserCulex(BowserPalette):
    colours = ["B0D8F8", "C09848", "B86028", "982818", "502010", "705090", "502870", "381048", "180808", "984818", "703010", "201008", "48A0D0", "205888", "102028"]
    poison_colours = ["D0C8F8", "B87080", "B04870", "8D2058", "481830", "785090", "582870", "381048", "180810", "903058", "682040", "200B10", "8070D0", "484088", "181828"]
    underwater_colours = ["5868B0", "604858", "583038", "481040", "281038", "382878", "281068", "180858", "080038", "482040", "381838", "100838", "205098", "102878", "081048"]
    name = "Culex"
    rename_character = False
class BowserWabowser(BowserPalette):
    colours = ["F8F8C0", "C8C8C8", "909090", "484848", "383838", "A880C8", "8860B0", "583080", "202020", "707070", "384858", "001018", "E0B860", "A88840", "382010"]
    poison_colours = ["F8A8F8", "D088F8", "9058F8", "382068", "281050", "A850F8", "8830F8", "5010D8", "100020", "6838B0", "282090", "000010", "E87098", "A85060", "280000"]
    underwater_colours = ["7C7C91", "646495", "484879", "242456", "1C1C4E", "544095", "443089", "2C1871", "101042", "383869", "1C245E", "00083E", "705C62", "544452", "18103A"]
    name = "Wabowser"
class BowserRed(BowserPalette):
    colours = ["F8F8F8", "D0D0D0", "F0C8C8", "B83838", "503838", "A83830", "782020", "481810", "202828", "C88080", "884848", "884848", "909090", "606060", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Red"
    rename_character = False
class BowserPink(BowserPalette):
    colours = ["F8F8F8", "F0A8A8", "E89088", "A86060", "501818", "E89088", "B86060", "501818", "200000", "A05860", "883030", "600808", "F8D0D0", "E08890", "200000"]
    poison_colours = []
    underwater_colours = []
    name = "Pink"
    rename_character = False
class BowserDark(BowserPalette):
    colours = ["F8F8F8", "F8F850", "F0C830", "B83810", "503818", "000000", "000000", "000000", "000000", "C88020", "884820", "201008", "909080", "606040", "181818"]
    poison_colours = ["A0F8F8", "A0F860", "98D028", "702800", "202800", "000000", "000000", "000000", "000000", "808018", "503818", "000000", "5090A8", "285848", "000000"]
    underwater_colours = ["82829A", "828246", "7E6A36", "622226", "2E222A", "05051E", "05051E", "05051E", "05051E", "6A462E", "4A2A2E", "160E22", "4E4E5E", "36363E", "12122A"]
    name = "Dark"
    rename_character = False
class BowserKronk(BowserPalette):
    colours = ["F8F080", "D8B8A0", "B89068", "383838", "181010", "D82830", "A81820", "600000", "300000", "886848", "704830", "201008", "D0B060", "806820", "482810"]
    poison_colours = []
    underwater_colours = []
    name = "Dark"
class BowserZeccet(BowserPalette):
    colours = ["F8F8F8", "f8d8b0", "e0b088", "703038", "481e24", "c84858", "a04068", "683858", "482840", "b08860", "886048", "201008", "909080", "606040", "181818"]
    poison_colours = ["A8F8F8", "A8E0F8", "98B0B0", "382038", "201018", "883868", "603088", "302868", "201848", "708870", "505850", "000000", "5890A8", "305848", "000000"]
    underwater_colours = ["7c7cad", "7c6c89", "705875", "38184e", "241042", "64245e", "502065", "341c5e", "241452", "584462", "443056", "100836", "484871", "303052", "0c0c3e"]
    name = "Zeccet"
class BowserDJN(BowserPalette):
    colours = ["F8F8F8", "CACEA5", "BCBB6F", "C76714", "21451C", "4E4EE8", "3D3DB8", "1818A5", "103008", "699C69", "387131", "201008", "909080", "606040", "181818"]
    poison_colours = ["F8E088", "E0B050", "D0A028", "E05000", "102800", "483080", "302860", "080050", "001800", "688828", "285808", "100000", "987040", "584810", "080000"]
    underwater_colours = ["7c7cad", "646885", "605c69", "64343a", "102442", "2828a5", "20208d", "0c0c85", "081836", "345065", "1c384a", "100836", "484871", "303052", "0c0c3e"]
    name = "DJNintendo"
#toadstool palettes
class ToadstoolDaisy(ToadstoolPalette):
    colours = ["F8F8F8", "E09870", "A86048", "402800", "502818", "F8C810", "F8A018", "D08800", "700000", "A85000", "903800", "0898A0", "C8C8D0", "786860", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Daisy"
class ToadstoolPauline(ToadstoolPalette):
    colours = ["F8F8F8", "E09870", "A86048", "402800", "180818", "F80010", "B80000", "700008", "700000", "A85000", "903800", "2848B0", "D0C8C8", "786860", "181818"]
    poison_colours = ["A8F8F8", "A8C8D8", "888890", "181800", "000000", "A80000", "700000", "380000", "380000", "684800", "582800", "0050F8", "88D0F8", "486070", "000000"]
    underwater_colours = ["7C7CAD", "7C6081", "684464", "201431", "0C0043D", "7C0039", "5C0031", "380035", "380031", "542831", "481C31", "142CA1", "686495", "3C3461", "0C0C3D"]
    name = "Pauline"
class ToadstoolRosalina(ToadstoolPalette):
    colours = ["F8F8F8", "F8E8B0", "E09870", "B06848", "102038", "80E0D8", "50A898", "207870", "002848", "F8D888", "F8A858", "2088D8", "D0C8C8", "786860", "181818"]
    poison_colours = ["E0F8B8", "E0F080", "C09848", "986028", "001018", "68E8A0", "38A868", "087048", "001828", "E0E058", "E0A838", "0888A0", "B0C890", "606040", "000800"]
    underwater_colours = ["7c7cad", "7c7489", "704c69", "583456", "08104e", "40709d", "28547d", "103c69", "001456", "7c6c75", "7c545e", "10449d", "686495", "3c3462", "0c0c3e"]
    name = "Rosalina"
class ToadstoolPalutena(ToadstoolPalette):
    colours = ["EBE3C8", "DDD0A2", "E09870", "1F4F21", "182818", "F2EEE9", "C0C4C8", "A12B1C", "5A4035", "6EB763", "3D863D", "902524", "CDB15F", "BA9101", "181818"]
    poison_colours = ["F8A0C8", "F89898", "F86860", "102810", "000000", "F8B0E8", "F888C8", "C80010", "602020", "888850", "385828", "B00010", "F88050", "E86000", "000000"]
    underwater_colours = ["747095", "706881", "704c69", "102842", "0c143e", "7878a5", "606095", "501442", "2c204e", "385c62", "204452", "481442", "685862", "5c4832", "0c0c3e"]
    name = "Palutena"
class ToadstoolKumatora(ToadstoolPalette):
    colours = ["F8F8F8", "F8C8C0", "E09870", "B02080", "282058", "70C0F8", "6090E0", "5070D0", "A82058", "F898F8", "E848B0", "380000", "A0A8C8", "686898", "181818"]
    poison_colours = ["A8F8B0", "A8E888", "98A848", "701050", "001028", "38E0B0", "30A0A0", "288090", "681028", "A8A8B0", "A04870", "100000", "60C888", "386860", "000000"]
    underwater_colours = ["7c7cad", "7c6491", "704c69", "581071", "14105e", "3860ad", "3048a1", "283899", "54105e", "7c4cad", "742489", "1c0032", "505495", "34347d", "0c0c3e"]
    name = "Kumatora"
class ToadstoolTia(ToadstoolPalette):
    colours = ["D8D0B8", "D8D0B8", "E4AB8B", "4060A0", "3B0857", "E67CA0", "F4518A", "D82E67", "B0B0B0", "90B0F8", "5888F0", "9F5C29", "E4AB8B", "C87840", "181818"]
    poison_colours = ["A0D8E8", "A0D8E8", "A0A8A8", "2058D0", "180060", "A880D0", "B048A8", "A02080", "80B0E0", "60B0F8", "3088F8", "685820", "A0A8A8", "907048", "000000"]
    underwater_colours = ["6c688d", "6c688d", "705475", "203081", "1c045e", "744081", "782875", "6c1865", "585889", "4858ad", "2c44a9", "503046", "705475", "643c52", "0c0c3e"]
    name = "Tia"
class ToadstoolKairi(ToadstoolPalette):
    colours = ["F8F8F8", "F8A0A0", "B87068", "300008", "383838", "F888A0", "D85070", "983048", "606060", "A82010", "701018", "1850C0", "D0C8C8", "786860", "181818"]
    poison_colours = ["F8F8F8", "F8A0C8", "B06890", "300018", "383838", "F088C8", "D050A0", "903070", "606060", "981858", "681040", "6038C0", "D0C8C8", "786868", "181818"]
    underwater_colours = ["7878B0", "785080", "583868", "180038", "181850", "784080", "682868", "481858", "303060", "501038", "380840", "082890", "686098", "383060", "080840"]
    name = "Kairi"
class ToadstoolLeena(ToadstoolPalette):
    colours = ["F8F8F8", "F8C088", "E09870", "A84800", "502818", "F83838", "C80808", "900000", "700000", "F8A060", "D87020", "706000", "D0B078", "A07840", "601818"]
    poison_colours = []
    underwater_colours = []
    name = "Leena"
class ToadstoolEmeralda(ToadstoolPalette):
    colours = ["F8E1D5", "E2C56C", "B67342", "47594C", "232323", "8D3121", "522118", "313131", "232323", "73B65A", "4A8463", "8B5E2E", "BB9A89", "A1877A", "181818"]
    poison_colours = ["F8B0F8", "F898A8", "D85058", "483070", "100020", "A01020", "500010", "201038", "100020", "809080", "485890", "983838", "D870D8", "C060B0", "000010"]
    underwater_colours = ["7c709d", "706469", "5c3852", "242c5a", "101042", "481842", "28103e", "18184a", "101042", "385c5e", "244062", "44304a", "5c4c75", "50446d", "0c0c3e"]
    name = "Emeralda"
class ToadstoolMiku(ToadstoolPalette):
    colours = ["F8F8F8", "F8F8E8", "E8C8B8", "108080", "103838", "606870", "404848", "182020", "00A0B8", "90D0D0", "48B8B8", "005050", "586060", "506060", "181818"]
    poison_colours = ["F8F8F8", "F8F0F0", "E0C0D0", "404880", "202838", "686070", "404848", "182020", "680038", "A8B0D0", "7880B8", "202850", "586060", "585860", "181818"]
    underwater_colours = ["7878B0", "7878A8", "706090", "084070", "081850", "303068", "202058", "081040", "380030", "486898", "205890", "002858", "283060", "283060", "080840"]
    name = "Miku"
class ToadstoolJasmine(ToadstoolPalette):
    colours = ["F8F8F8", "B88868", "806848", "402810", "001820", "80E8D8", "50A898", "207868", "002848", "805838", "583810", "305040", "D0C8C8", "786860", "181818"]
    poison_colours = ["F8A8F8", "C050D0", "803088", "300000", "000028", "8098F8", "4868F8", "1048D0", "000088", "802860", "501000", "202070", "D888F8", "7030C0", "000018"]
    underwater_colours = ["7C7CAD", "5C4465", "403456", "20143A", "000C42", "40749D", "28547D", "103C65", "001456", "402C4E", "2C1C3A", "182852", "686495", "3C3462", "0C0C3E"]
    name = "Jasmine"
class ToadstoolKotori(ToadstoolPalette):
    colours = ["F8F8F8", "F2D6A2", "C1A268", "715D42", "383818", "BEE7CB", "70CA8B", "3A935C", "236040", "C3AE8F", "A2937F", "6F521E", "D0C8C8", "786860", "181818"]
    poison_colours = ["F8D0F8", "F8A8D0", "D08080", "703848", "281800", "D0C0F8", "70A0A8", "286870", "103848", "D088B0", "A868A0", "703018", "E8A0F8", "804870", "000000"]
    underwater_colours = ["7c7cad", "786c81", "605065", "383052", "1c1c3e", "607495", "386475", "1c4862", "103052", "605879", "504871", "382842", "686495", "3c3462", "0c0c3e"]
    name = "Kotori"
class ToadstoolZombie(ToadstoolPalette):
    colours = ["F8E0D0", "A0C090", "809850", "385040", "000000", "987868", "806050", "604028", "101010", "689028", "486838", "700000", "C0A888", "785840", "181818"]
    poison_colours = []
    underwater_colours = []
    name = "Zombie"
    rename_character = False
class ToadstoolBlood(ToadstoolPalette):
    colours = ["F8F8F8", "F8E8B0", "E09870", "985010", "602818", "F8F8F8", "D00000", "900000", "700000", "F8D038", "F88820", "3838D0", "D0C8C8", "786860", "300000"]
    poison_colours = []
    underwater_colours = []
    name = "Blood Peach"
    rename_character = False
class ToadstoolDemon(ToadstoolPalette):
    colours = []
    poison_colours = []
    underwater_colours = []
    name = "Demon"
    rename_character = False
class ToadstoolRed(ToadstoolPalette):
    colours = ["F8F8F8", "F8E8B0", "E09870", "883800", "401808", "C84C5B", "A22635", "770F19", "700000", "F8D038", "D86800", "4a9dbe", "D0C8C8", "786860", "181818"]
    poison_colours = ["A0F8F8", "A0F8E8", "90B090", "986030", "281808", "805870", "682848", "501018", "480000", "E0D028", "B0A018", "30B8F8", "88E8F8", "507878", "101818"]
    underwater_colours = ["7c7cad", "7c7489", "704c69", "441c32", "200c36", "64285e", "50144e", "3c083e", "380032", "7c684e", "6c3432", "245091", "686495", "3c3462", "0c0c3e"]
    name = "Red"
    rename_character = False
class ToadstoolGreen(ToadstoolPalette):
    colours = []
    poison_colours = []
    underwater_colours = []
    name = "Green"
    rename_character = False
class ToadstoolBlue(ToadstoolPalette):
    colours = []
    poison_colours = []
    underwater_colours = []
    name = "Blue"
    rename_character = False
class ToadstoolBlack(ToadstoolPalette):
    colours = []
    poison_colours = []
    underwater_colours = []
    name = "Black"
    rename_character = False