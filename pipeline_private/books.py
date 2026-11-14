"""Two catalogues with different rules: public domain, and in-copyright private use.

The split is a legal fact, not a preference. China protects a work for fifty years from
the end of the year of the author's death, so with the current year at 2026 anything by
an author who died in 1975 or earlier is free to publish and attribute, and anything
later is not.

An earlier draft of this file put Kafka, Rilke, Woolf and Hofmannsthal in the private
list. All four died before 1975, so all four are public domain -- the private list was
testing nothing. They are corrected here and moved to the public catalogue, where they
belong and where they are worth adding: Kafka in particular has no complete Chinese
edition of the three novels from a single hand.

The in-copyright list starts at 1976 and runs to the present. Those translations are for
reading only: no translator credit, no licence claim, no output in `./out`.
"""
from __future__ import annotations

CURRENT_YEAR = 2026
# Fifty years counted from the end of the year of death: an author who died in 1976 stays
# protected through 2026-12-31. The last fully lapsed year is therefore 2025 - 50.
PUBLIC_CUTOFF = CURRENT_YEAR - 51      # died <= 1975 -> public

# --- public domain: publishable, credited to 坟头草 ---------------------------------
# High-value additions rather than obscure titles: works a Chinese reader has heard of
# and cannot currently read in a complete, consistent translation.
PUBLIC = [
    dict(key="verwandlung", title_zh="变形记", title_src="Die Verwandlung",
         author_zh="弗朗茨·卡夫卡", author_src="Franz Kafka", lang="de", died=1924,
         gid=22367, note="德语中篇；Gutenberg 德文原版"),
    dict(key="prozess", title_zh="诉讼", title_src="Der Prozess: Roman",
         author_zh="弗朗茨·卡夫卡", author_src="Franz Kafka", lang="de", died=1924,
         gid=69327, note="德语长篇，未完成"),
    dict(key="urteil", title_zh="判决", title_src="Das Urteil: Eine Geschichte",
         author_zh="弗朗茨·卡夫卡", author_src="Franz Kafka", lang="de", died=1924,
         gid=21593, note="德语短篇"),
    dict(key="strafkolonie", title_zh="在流放地", title_src="In der Strafkolonie",
         author_zh="弗朗茨·卡夫卡", author_src="Franz Kafka", lang="de", died=1924,
         gid=25791, note="德语短篇"),
    dict(key="landarzt", title_zh="乡村医生",
         title_src="Ein Landarzt: Kleine Erzählungen",
         author_zh="弗朗茨·卡夫卡", author_src="Franz Kafka", lang="de", died=1924,
         gid=21989, note="德语短篇集，十四篇"),
    dict(key="hungerkuenstler", title_zh="饥饿艺术家",
         title_src="Ein Hungerkünstler", author_zh="弗朗茨·卡夫卡",
         author_src="Franz Kafka", lang="de", died=1924, gid=30655,
         note="德语短篇集"),
    dict(key="betrachtung", title_zh="观察", title_src="Betrachtung",
         author_zh="弗朗茨·卡夫卡", author_src="Franz Kafka", lang="de", died=1924,
         gid=23532, note="德语短篇集，首部出版作品"),
    dict(key="malte", title_zh="马尔特手记",
         title_src="Die Aufzeichnungen des Malte Laurids Brigge",
         author_zh="赖内·马利亚·里尔克", author_src="Rainer Maria Rilke", lang="de",
         died=1926, gid=2188, note="德语长篇；里尔克唯一长篇小说"),
    dict(key="stundenbuch", title_zh="时祷书", title_src="Das Stunden-Buch",
         author_zh="赖内·马利亚·里尔克", author_src="Rainer Maria Rilke", lang="de",
         died=1926, gid=24288, note="德语诗集"),
    dict(key="neuegedichte", title_zh="新诗集", title_src="Neue Gedichte",
         author_zh="赖内·马利亚·里尔克", author_src="Rainer Maria Rilke", lang="de",
         died=1926, gid=33863, note="德语诗集"),
    dict(key="mrsdalloway", title_zh="达洛维夫人", title_src="Mrs. Dalloway",
         author_zh="弗吉尼亚·伍尔夫", author_src="Virginia Woolf", lang="en",
         died=1941, gid=71865, note="英语长篇，意识流"),
    dict(key="jacobsroom", title_zh="雅各的房间", title_src="Jacob's Room",
         author_zh="弗吉尼亚·伍尔夫", author_src="Virginia Woolf", lang="en",
         died=1941, gid=5670, note="英语长篇"),
    dict(key="mondaytuesday", title_zh="星期一或星期二", title_src="Monday or Tuesday",
         author_zh="弗吉尼亚·伍尔夫", author_src="Virginia Woolf", lang="en",
         died=1941, gid=29220, note="英语短篇集"),
    dict(key="voyageout", title_zh="远航", title_src="The Voyage Out",
         author_zh="弗吉尼亚·伍尔夫", author_src="Virginia Woolf", lang="en",
         died=1941, gid=144, note="英语长篇，首部长篇"),
    dict(key="jedermann", title_zh="每个人",
         title_src="Jedermann: Das Spiel vom Sterben des reichen Mannes",
         author_zh="胡戈·冯·霍夫曼斯塔尔", author_src="Hugo von Hofmannsthal",
         lang="de", died=1929, gid=28949, note="德语剧本", one_act=True),
    dict(key="torundtod", title_zh="愚者与死神", title_src="Der Tor und der Tod",
         author_zh="胡戈·冯·霍夫曼斯塔尔", author_src="Hugo von Hofmannsthal",
         lang="de", died=1929, gid=31850, note="德语诗剧", one_act=True),
    # --- second batch, added 2026-10-26 ------------------------------------------------
    # Every gid below was checked against the catalogue's own `dcterms:language`
    # attribute before being accepted. That check is not ceremony: the obvious ids for
    # War and Peace (2600), Crime and Punishment (2554), Notre-Dame (2610) and Le Père
    # Goriot (1237) all resolve to **English translations**, and translating those into
    # Chinese would be translating a translation. Gutenberg's `?lang=` search parameter
    # is decorative -- "Tolstoy&lang=ru" returns the English edition -- so the only
    # reliable test is the edition's own metadata. Russian classics were dropped
    # entirely: the originals are not in the catalogue.
    dict(key="bovary", title_zh="包法利夫人", title_src="Madame Bovary",
         author_zh="居斯塔夫·福楼拜", author_src="Gustave Flaubert", lang="fr",
         died=1880, gid=14155, note="法语长篇；Gutenberg 法文原版"),
    dict(key="rouge", title_zh="红与黑", title_src="Le Rouge et le Noir",
         author_zh="司汤达", author_src="Stendhal", lang="fr", died=1842,
         gid=798, note="法语长篇，副题《一八三〇年纪事》"),
    dict(key="montecristo", title_zh="基督山伯爵",
         title_src="Le Comte de Monte-Cristo", author_zh="大仲马",
         author_src="Alexandre Dumas", lang="fr", died=1870, gid=17989,
         note="法语长篇；分部本，首部"),
    dict(key="musketeers", title_zh="三个火枪手",
         title_src="Les Trois Mousquetaires", author_zh="大仲马",
         author_src="Alexandre Dumas", lang="fr", died=1870, gid=13951,
         note="法语长篇"),
    dict(key="notredame", title_zh="巴黎圣母院", title_src="Notre-Dame de Paris",
         author_zh="维克多·雨果", author_src="Victor Hugo", lang="fr", died=1885,
         gid=70891, note="法语长篇"),
    dict(key="miserables", title_zh="悲惨世界", title_src="Les Misérables",
         author_zh="维克多·雨果", author_src="Victor Hugo", lang="fr", died=1885,
         gid=17489, note="法语长篇；分部本，首部《芳汀》"),
    dict(key="goriot", title_zh="高老头", title_src="Le Père Goriot",
         author_zh="奥诺雷·德·巴尔扎克", author_src="Honoré de Balzac", lang="fr",
         died=1850, gid=55860,
         note="法语长篇；《人间喜剧》；源文无分章标记",
         one_act=True),
    dict(key="horla", title_zh="奥尔拉", title_src="Le Horla",
         author_zh="居伊·德·莫泊桑", author_src="Guy de Maupassant", lang="fr",
         died=1893, gid=10775, note="法语短篇集"),
    dict(key="buddenbrooks", title_zh="布登勃洛克一家", title_src="Budenbrooks",
         author_zh="托马斯·曼", author_src="Thomas Mann", lang="de", died=1955,
         gid=34811, note="德语长篇；副题《一个家庭的没落》"),
    dict(key="siddhartha", title_zh="悉达多", title_src="Siddhartha",
         author_zh="赫尔曼·黑塞", author_src="Hermann Hesse", lang="de",
         died=1962, gid=2499, note="德语中篇；副题《一首印度的诗》"),
    dict(key="faust", title_zh="浮士德", title_src="Faust: Der Tragödie erster Teil",
         author_zh="约翰·沃尔夫冈·冯·歌德",
         author_src="Johann Wolfgang von Goethe", lang="de", died=1832,
         gid=2229, note="德语诗剧，第一部", one_act=True),
    dict(key="toerless", title_zh="学生托勒斯的迷惘",
         title_src="Die Verwirrungen des Zöglings Törleß", author_zh="罗伯特·穆齐尔",
         author_src="Robert Musil", lang="de", died=1942, gid=34717,
         note="德语中篇；穆齐尔唯一完成的长篇"),
    dict(key="pride", title_zh="傲慢与偏见", title_src="Pride and Prejudice",
         author_zh="简·奥斯汀", author_src="Jane Austen", lang="en", died=1817,
         gid=1342, note="英语长篇"),
    dict(key="emma", title_zh="爱玛", title_src="Emma",
         author_zh="简·奥斯汀", author_src="Jane Austen", lang="en", died=1817,
         gid=158, note="英语长篇，副题《一部带主观偏见的小说》"),
    dict(key="persuasion", title_zh="劝导", title_src="Persuasion",
         author_zh="简·奥斯汀", author_src="Jane Austen", lang="en", died=1817,
         gid=105, note="英语长篇，身后出版"),
    dict(key="twocities", title_zh="双城记", title_src="A Tale of Two Cities",
         author_zh="查尔斯·狄更斯", author_src="Charles Dickens", lang="en",
         died=1870, gid=98, note="英语长篇，历史小说"),
    dict(key="expectations", title_zh="远大前程", title_src="Great Expectations",
         author_zh="查尔斯·狄更斯", author_src="Charles Dickens", lang="en",
         died=1870, gid=1400, note="英语长篇，成长小说"),
    dict(key="bleakhouse", title_zh="荒凉山庄", title_src="Bleak House",
         author_zh="查尔斯·狄更斯", author_src="Charles Dickens", lang="en",
         died=1870, gid=1023, note="英语长篇；本批篇幅最长"),
    dict(key="tess", title_zh="德伯家的苔丝",
         title_src="Tess of the d'Urbervilles", author_zh="托马斯·哈代",
         author_src="Thomas Hardy", lang="en", died=1928, gid=110,
         note="英语长篇，副题《一个纯洁的女人》"),
    dict(key="jude", title_zh="无名的裘德", title_src="Jude the Obscure",
         author_zh="托马斯·哈代", author_src="Thomas Hardy", lang="en", died=1928,
         gid=153, note="英语长篇；哈代封笔之作"),
    dict(key="darkness", title_zh="黑暗的心", title_src="Heart of Darkness",
         author_zh="约瑟夫·康拉德", author_src="Joseph Conrad", lang="en",
         died=1924, gid=219, note="英语中篇"),
    dict(key="dubliners", title_zh="都柏林人", title_src="Dubliners",
         author_zh="詹姆斯·乔伊斯", author_src="James Joyce", lang="en", died=1941,
         gid=2814, note="英语短篇集，十五篇"),
]

# --- in copyright: private reading only, never published ----------------------------
# Death year after 1975. Deliberately weighted towards writers with major standing and no
# trustworthy Chinese version, so the translation is worth the effort even unshareable.
IN_COPYRIGHT = [
    dict(key="lispector", title_zh="星辰时刻", title_src="A Hora da Estrela",
         author_zh="克拉丽斯·李斯佩克朵", author_src="Clarice Lispector", lang="pt",
         died=1977, note="葡萄牙语长篇；作者 1977 年去世，仍在保护期"),
    dict(key="shalamov", title_zh="科雷马故事", title_src="Колымские рассказы",
         author_zh="瓦尔拉姆·沙拉莫夫", author_src="Varlam Shalamov", lang="ru",
         died=1982, note="俄语短篇集"),
    dict(key="cortazar", title_zh="跳房子", title_src="Rayuela",
         author_zh="胡利奥·科塔萨尔", author_src="Julio Cortázar", lang="es",
         died=1984, note="西班牙语长篇，结构小说"),
    dict(key="calvino", title_zh="如果在冬夜，一个旅人",
         title_src="Se una notte d'inverno un viaggiatore",
         author_zh="伊塔洛·卡尔维诺", author_src="Italo Calvino", lang="it",
         died=1985, note="意大利语长篇"),
    dict(key="rulfo", title_zh="佩德罗·巴拉莫", title_src="Pedro Páramo",
         author_zh="胡安·鲁尔福", author_src="Juan Rulfo", lang="es", died=1986,
         note="西班牙语长篇；魔幻现实主义源头"),
    dict(key="levi", title_zh="元素周期表", title_src="Il sistema periodico",
         author_zh="普里莫·莱维", author_src="Primo Levi", lang="it", died=1987,
         note="意大利语短篇集"),
    dict(key="yourcenar", title_zh="哈德良回忆录",
         title_src="Mémoires d'Hadrien", author_zh="玛格丽特·尤瑟纳尔",
         author_src="Marguerite Yourcenar", lang="fr", died=1987, note="法语长篇"),
    dict(key="bernhard", title_zh="伐木", title_src="Holzfällen",
         author_zh="托马斯·伯恩哈德", author_src="Thomas Bernhard", lang="de",
         died=1989, note="德语长篇"),
    dict(key="beckett", title_zh="无法称呼的人", title_src="L'Innommable",
         author_zh="萨缪尔·贝克特", author_src="Samuel Beckett", lang="fr",
         died=1989, note="法语长篇"),
    dict(key="kis", title_zh="墓志铭", title_src="Grobnica za Borisa Davidoviča",
         author_zh="达尼洛·基什", author_src="Danilo Kiš", lang="sr", died=1989,
         note="塞尔维亚语短篇集"),
    dict(key="sciascia", title_zh="白天的猫头鹰", title_src="Il giorno della civetta",
         author_zh="莱奥纳尔多·夏侠", author_src="Leonardo Sciascia", lang="it",
         died=1989, note="意大利语长篇"),
    dict(key="ginzburg", title_zh="家庭絮语", title_src="Lessico famigliare",
         author_zh="娜塔莉亚·金兹伯格", author_src="Natalia Ginzburg", lang="it",
         died=1991, note="意大利语长篇"),
    dict(key="canetti", title_zh="迷惘", title_src="Die Blendung",
         author_zh="埃利亚斯·卡内蒂", author_src="Elias Canetti", lang="de",
         died=1994, note="德语长篇"),
    dict(key="duras", title_zh="情人", title_src="L'Amant",
         author_zh="玛格丽特·杜拉斯", author_src="Marguerite Duras", lang="fr",
         died=1996, note="法语长篇"),
    dict(key="brodsky", title_zh="约瑟夫·布罗茨基诗选", title_src="Стихотворения",
         author_zh="约瑟夫·布罗茨基", author_src="Joseph Brodsky", lang="ru",
         died=1996, note="俄语诗歌"),
    dict(key="koeppen", title_zh="草中之鸽", title_src="Tauben im Gras",
         author_zh="沃尔夫冈·克彭", author_src="Wolfgang Koeppen", lang="de",
         died=1996, note="德语长篇"),
    dict(key="hrabal", title_zh="我曾侍候过英国国王",
         title_src="Obsluhoval jsem anglického krále",
         author_zh="博胡米尔·赫拉巴尔", author_src="Bohumil Hrabal", lang="cs",
         died=1997, note="捷克语长篇"),
    dict(key="herbert", title_zh="科吉托先生诗选", title_src="Pan Cogito",
         author_zh="兹比格涅夫·赫伯特", author_src="Zbigniew Herbert", lang="pl",
         died=1998, note="波兰语诗歌"),
    dict(key="paz", title_zh="太阳石", title_src="Piedra de Sol",
         author_zh="奥克塔维奥·帕斯", author_src="Octavio Paz", lang="es",
         died=1998, note="西班牙语长诗"),
    dict(key="sebald", title_zh="奥斯特利茨", title_src="Austerlitz",
         author_zh="W. G. 泽巴尔德", author_src="W. G. Sebald", lang="de",
         died=2001, note="德语长篇"),
    dict(key="bolano", title_zh="2666", title_src="2666",
         author_zh="罗贝托·波拉尼奥", author_src="Roberto Bolaño", lang="es",
         died=2003, note="西班牙语长篇"),
    dict(key="milosz", title_zh="米沃什诗选", title_src="Wiersze",
         author_zh="切斯瓦夫·米沃什", author_src="Czesław Miłosz", lang="pl",
         died=2004, note="波兰语诗歌"),
    dict(key="wolf", title_zh="卡桑德拉", title_src="Kassandra",
         author_zh="克里斯塔·沃尔夫", author_src="Christa Wolf", lang="de",
         died=2011, note="德语长篇"),
    dict(key="szymborska", title_zh="辛波斯卡诗选", title_src="Wiersze",
         author_zh="维斯拉瓦·辛波斯卡", author_src="Wisława Szymborska", lang="pl",
         died=2012, note="波兰语诗歌"),
    dict(key="kundera", title_zh="不能承受的生命之轻",
         title_src="Nesnesitelná lehkost bytí",
         author_zh="米兰·昆德拉", author_src="Milan Kundera", lang="cs",
         died=2023, note="捷克语长篇"),
]


def is_public(died: int) -> bool:
    """True when the author's works are out of copyright in China."""
    return 0 < died <= PUBLIC_CUTOFF


def classify() -> tuple:
    """Split both catalogues, so nothing in copyright can drift into the public line."""
    public = [b for b in PUBLIC if is_public(b["died"])]
    # anything in PUBLIC that fails the check is reported rather than silently published
    misplaced = [b for b in PUBLIC if not is_public(b["died"])]
    private = list(IN_COPYRIGHT)
    return public, private, misplaced


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    pub, priv, bad = classify()
    print(f"public cutoff: died <= {PUBLIC_CUTOFF}\n")
    print(f"PUBLIC (publishable, credited): {len(pub)}")
    for b in pub:
        print(f"  {b['key']:14s} {b['title_zh']:16s} {b['author_zh']:16s} "
              f"died {b['died']}")
    print(f"\nIN COPYRIGHT (private only): {len(priv)}")
    for b in priv:
        print(f"  {b['key']:14s} {b['title_zh']:16s} {b['author_zh']:16s} "
              f"died {b['died']}")
    if bad:
        print(f"\nWARNING misplaced in PUBLIC: {[b['key'] for b in bad]}")
