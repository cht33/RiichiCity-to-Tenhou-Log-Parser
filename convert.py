# -*- coding: utf-8 -*-
import json

# 掌心麻将 id to tenhou6 id
def zxid_to_thid(zx_id: int):
    # 掌心麻将的id映射关系
    # 0x01-0x09 1p-9p
    # 0x11-0x19 1s-9s
    # 0x21-0x29 1m-9m
    # 0x31-0x91 1z-7z
    # 0x105-0x125 0p0s0m

    # tenhou6 id的映射关系
    # 11-19 1m-9m
    # 21-29 1p-9p
    # 31-39 1s-9s
    # 41-47 1z-7z
    # 51-53 0m0p0s

    if zx_id == 0x00:
        return 0
    elif zx_id >= 0x01 and zx_id <= 0x09:
        return (zx_id % 16) + 20
    elif zx_id >= 0x11 and zx_id <= 0x19:
        return (zx_id % 16) + 30
    elif zx_id >= 0x21 and zx_id <= 0x29:
        return (zx_id % 16) + 10
    elif zx_id >= 0x31 and zx_id <= 0x91:
        return (zx_id // 16) - 2 + 40
    elif zx_id == 0x105:
        return 52
    elif zx_id == 0x115:
        return 53
    elif zx_id == 0x125:
        return 51
    else:
        raise ValueError(f"Invalid ZX ID: {zx_id}")

# 牌山字符串 to tenhou6 id
def thstr_to_thid(card: str):
    # tenhou6 id的映射关系
    # 11-19 1m-9m
    # 21-29 1p-9p
    # 31-39 1s-9s
    # 41-47 1z-7z
    # 51-53 0m0p0s
    a = ['m', 'p', 's', 'z'].index(card[1]) + 1
    b = int(card[0])
    if b == 0:
        thid = 50 + a
    else:
        thid = a * 10 + b
    return thid

TENHOU6_BASE_URL = "https://tenhou.net/6/#json="

# 掌心麻将的番种映射到天凤的番种
Yakus = {
  0: '立直',
  1: '门清自摸',
  2: '一发',
  3: '岭上开花',
  4: '海底捞月',
  5: '河底捞鱼',
  6: '抢杠',
  7: '役牌：中',
  8: '役牌：发',
  9: '役牌：白',
  10: '役牌：场风牌',
  11: '役牌：自风牌',
  12: '一杯口',
  13: '平和',
  14: '断幺九',
  15: '双立直',
  16: '对对和',
  17: '七对子',
  18: '三暗刻',
  19: '三杠子',
  20: '混老头',
  21: '混全带幺九',
  22: '一气通贯',
  23: '三色同顺',
  24: '小三元',
  25: '三色同刻',
  26: '纯全带幺九',
  27: '混一色',
  28: '二杯口',
  29: '清一色',
  30: '流局满贯',
  31: '天和',
  32: '地和',
  33: '人和',
  34: '国士无双',
  35: '国士无双十三面',
  36: '九莲宝灯',
  37: '纯正九莲宝灯',
  38: '四暗刻',
  39: '四暗刻单骑',
  40: '四杠子',
  41: '清老头',
  42: '字一色',
  43: '大四喜',
  44: '小四喜',
  45: '大三元',
  46: '绿一色',
  47: '无发绿一色',
  48: '八连庄',
  49: '赤宝牌',
  50: '宝牌',
  51: '里宝牌',
  52: '开立直',
  53: '开双立直',
  54: '开立直',
  55: '拔北宝牌',
  56: '役牌：北',
}

# 读取掌心麻将的日志并将其转换成tenhou6的json格式
def convert(input_file, output_file):
    # 读取日志文件
    with open(input_file, 'r', encoding='utf-8') as f:
        zx_data = json.load(f)

    tenhou_game_log = {}
    tenhou_game_log["rule"] = { "aka": 1, "disp": "4-Player South"}
    tenhou_game_log["title"] = ["zhangxinmj", "4-Player South"]
    tenhou_game_log["log"] = []
    tenhou6_url_list = []

    # 解析日志文件
    handRecord = zx_data.get("handRecord", [])

    # 解析玩家信息
    players = handRecord[0].get("players", [])
    # 将 userId 映射到 nickname
    player_id_list = [0, 0, 0, 0]
    player_name_map = {}
    total_points = 0
    for player in players:
        userId = player.get("userId")
        nickname = player.get("nickname")
        player_name_map[userId] = nickname
        player_id_list[player["position"]] = userId
        total_points += player.get("points")

    # 找到东一局的起始玩家
    event = {}
    for e in handRecord[0]["handEventRecord"]:
        eventType = e.get("eventType")
        if eventType == 2:
            event = e
            break
    first_user_id = event.get("userId")
    first_user_position = player_id_list.index(first_user_id)
    player_id_list = player_id_list[first_user_position:] + player_id_list[:first_user_position]
    player_name_list = [player_name_map[userId] for userId in player_id_list]
    tenhou_game_log["name"] = player_name_list

    for record in handRecord:
        player_game_log = {
            userId: {
                "hand_cards": [],
                "draw_cards": [],
                "discard_cards": [],
                "hand_cards_num": 13,
            } for userId in player_id_list
        }
        players = record.get("players", [])
        benChangNum = record.get("benChangNum", None)
        changCi = record.get("changCi", None) - 1

        quanFeng = record.get("quanFeng", 0)
        quanFeng = zxid_to_thid(quanFeng)
        changCi += (quanFeng - 41) * 4

        print(changCi, benChangNum)

        log = []
        point_list = [player.get("points") for player in players]
        lizhibang_num = (total_points - sum(point_list)) // 1000
        log.append([changCi, benChangNum, lizhibang_num])
        log.append(point_list)

        # 解析宝牌指示牌和里宝指示牌
        paiShan = record.get("paiShan", "")
        baopai = [paiShan[-5], paiShan[-7], paiShan[-9], paiShan[-11]]
        libaopai = [paiShan[-6], paiShan[-8], paiShan[-10], paiShan[-12]]
        baopai = [zxid_to_thid(card) for card in baopai]
        libaopai = [zxid_to_thid(card) for card in libaopai]
        log.append(baopai)
        log.append(libaopai)

        out_card_userId = 0
        last_in_card = 0
        end_info = []

        for event in record["handEventRecord"]:
            eventType = event.get("eventType")
            userId = event.get("userId")

            data = event.get("data", "")
            data = json.loads(data)

            if eventType == 1:  # 1表示开局手牌
                # 将手牌转换为tenhou6的格式
                hand_cards = data.get("hand_cards", [])
                hand_cards = [zxid_to_thid(card) for card in hand_cards]
                # print(f"Event Type: {eventType}, nickname: {player_name_map.get(userId, 'Unknown')}")
                # print(hand_cards)

                # 切分庄家起始手牌
                if changCi % 4 == player_id_list.index(userId):
                    player_game_log[userId]["draw_cards"].append(hand_cards[-1])
                    hand_cards = hand_cards[:-1]
                player_game_log[userId]["hand_cards"] = hand_cards

            elif eventType == 2: # 2表示摸牌
                in_card = data.get("in_card")
                in_card = zxid_to_thid(in_card)
                last_in_card = in_card
                if in_card == 0: continue
                player_game_log[userId]["draw_cards"].append(in_card)
                # print(f"Event Type: {eventType}, nickname: {player_name_map.get(userId, 'Unknown')}, Draw Card: {in_card}")

            elif eventType == 3: # outcard，鸣牌等待事件
                continue

            elif eventType == 4: # 4表示动作
                action = data.get("action")

                if action == 11: # 11表示打牌
                    out_card = data.get("card")
                    out_card = zxid_to_thid(out_card)
                    # 如果当前切牌位置是最右侧的牌则表示摸切
                    move_cards_pos = data.get("move_cards_pos", None)

                    # 日志有时候会丢失切牌位置，这种情况暂且默认是摸切
                    if move_cards_pos is None:
                        out_card = 60 # 60表示摸切
                    elif last_in_card != 0 and move_cards_pos[0] == player_game_log[userId]["hand_cards_num"] + 1:
                        out_card = 60 # 60表示摸切

                    if data["is_li_zhi"]:
                        out_card = f"r{out_card}"
                    player_game_log[userId]["discard_cards"].append(out_card)
                    out_card_userId = userId

                elif action == 2 or action == 3 or action == 4: # 234表示吃牌
                    player_game_log[userId]["hand_cards_num"] -= 3
                    in_card = data.get("card")
                    in_card = zxid_to_thid(in_card)
                    group_cards = data.get("group_cards", [])
                    group_cards = [zxid_to_thid(card) for card in group_cards]
                    chi_info = f"c{in_card}{group_cards[0]}{group_cards[1]}"
                    player_game_log[userId]["draw_cards"].append(chi_info)

                elif action == 5: # 5表示碰牌
                    player_game_log[userId]["hand_cards_num"] -= 3
                    in_card = data.get("card")
                    in_card = zxid_to_thid(in_card)
                    in_idx = player_id_list.index(userId)
                    out_idx = player_id_list.index(out_card_userId)
                    p_idx = (in_idx - out_idx + 4) % 4 - 1

                    group_cards = data.get("group_cards", [])
                    group_cards = [str(zxid_to_thid(card)) for card in group_cards]
                    group_cards.insert(p_idx ,"p" + str(in_card))
                    peng_info = "".join(group_cards)
                    player_game_log[userId]["draw_cards"].append(peng_info)

                elif action == 6: # 6表示明杠
                    player_game_log[userId]["hand_cards_num"] -= 3
                    in_card = data.get("card")
                    in_card = zxid_to_thid(in_card)
                    in_idx = player_id_list.index(userId)
                    out_idx = player_id_list.index(out_card_userId)
                    k_idx = (in_idx - out_idx + 4) % 4 - 1
                    # tenhou6的明杠形式非对称，分别为：
                    # m12121212 上家
                    # 12m121212 对家
                    # 121212m12 下家
                    if k_idx == 2: k_idx += 1

                    group_cards = data.get("group_cards", [])
                    group_cards = [str(zxid_to_thid(card)) for card in group_cards]
                    group_cards.insert(k_idx, "m" + str(in_card))
                    kang_info = "".join(group_cards)
                    player_game_log[userId]["draw_cards"].append(kang_info)
                    player_game_log[userId]["discard_cards"].append(0)

                elif action == 7 or action == 10: # 7荣胡，10自摸，无需处理
                    continue

                elif action == 8: # 8表示暗杠
                    player_game_log[userId]["hand_cards_num"] -= 3
                    card = data.get("card")
                    card = zxid_to_thid(card)
                    group_cards = data.get("group_cards", [])
                    group_cards = [str(card)] + [str(zxid_to_thid(c)) for c in group_cards]
                    group_cards.insert(3, "a")
                    kang_info = "".join(group_cards)
                    player_game_log[userId]["discard_cards"].append(kang_info)

                elif action == 9: # 9表示补杠
                    in_card = data.get("card")
                    in_card = zxid_to_thid(in_card)
                    target_card = in_card
                    if in_card > 50: # 特殊处理补杠赤宝牌的情况
                        target_card = (in_card - 50) * 10 + 5
                    bu_kang_info = ""
                    for s in player_game_log[userId]["draw_cards"]:
                        if isinstance(s, str) and s.count(str(target_card)) == 3:
                            bu_kang_info = s
                            break
                    bu_kang_info = list(bu_kang_info.replace('p', 'k'))
                    bu_kang_info.insert(bu_kang_info.index('k')+1, str(in_card))
                    bu_kang_info = "".join(bu_kang_info)
                    player_game_log[userId]["discard_cards"].append(bu_kang_info)

                else:
                    print(f"Unknown action: {event}")

            elif eventType == 5: # 5表示结束
                user_profit = data.get("user_profit", [])
                delta_points = [0, 0, 0, 0]
                for profit in user_profit:
                    userId = profit.get("user_id")
                    profit = profit.get("point_profit")
                    delta_points[player_id_list.index(userId)] = profit

                end_type = data.get("end_type")
                if end_type == 0: # 0表示放铳
                    # 找到 delta_points 中大于0和小于0的下标位置
                    positive_idx = [i for i, x in enumerate(delta_points) if x > 0]
                    negative_idx = [i for i, x in enumerate(delta_points) if x < 0]

                    if len(data["win_info"]) == 1: # 只铳一家
                        end_info = [
                            "和了",
                            delta_points,
                            [positive_idx[0], negative_idx[0], negative_idx[0]],
                        ]
                    elif len(data["win_info"]) == 2: # 一炮双响
                        lose_idx = negative_idx[0]
                        if negative_idx[0] > positive_idx[0] and negative_idx[0] < positive_idx[1]:
                            win_idx1, win_idx2 = positive_idx[-1::-1]
                        else:
                            win_idx1, win_idx2 = positive_idx
                        lose_point2 = -delta_points[win_idx2]
                        lose_point1 = delta_points[lose_idx] - lose_point2
                        delta_points1, delta_points2 = [0]*4, [0]*4
                        delta_points1[win_idx1] = delta_points[win_idx1]
                        delta_points1[lose_idx] = lose_point1
                        delta_points2[win_idx2] = delta_points[win_idx2]
                        delta_points2[lose_idx] = lose_point2
                        end_info = [
                            "和了",
                            delta_points1,
                            [win_idx1, lose_idx, win_idx1],
                            delta_points2,
                            [win_idx2, lose_idx, win_idx2],
                        ]

                elif end_type == 1: # 1表示自摸
                    positive_idx = [i for i, x in enumerate(delta_points) if x > 0]
                    end_info = [
                        "和了",
                        delta_points,
                        [positive_idx[0], positive_idx[0], positive_idx[0]],
                    ]
                elif end_type == 7: # 7表示流局
                    end_info = [ "流局", delta_points]
                else:
                    print(f"Unknown end type: {event}")

                # TODO: 解析番种信息
                # win_info = data.get("win_info", [])
                # for info in win_info:
                #     fang_info = info.get("fang_info", {})
                # print(data)

            elif eventType == 6 or eventType == 7 or eventType == 8 or eventType == 9 or eventType == 11:
                # 6表示半庄结束事件
                # 7表示翻杠宝牌事件
                # 8表示立直自动开杠事件
                # 9表示见逃、无役等无法胡牌的事件
                # 11表示立直后听牌信息
                continue

            else:
                print(f"Unknown event type: {event}")

        for userId in player_id_list:
            log.append(player_game_log[userId]["hand_cards"])
            log.append(player_game_log[userId]["draw_cards"])
            log.append(player_game_log[userId]["discard_cards"])
        log.append(end_info)
        tenhou_game_log["log"] = [log]

        # 将日志转换成url，json中无空格
        # tenhou6_url = base_url + urlencode({"json": tenhou_game_log})
        tenhou6_url = TENHOU6_BASE_URL + json.dumps(tenhou_game_log, separators=(',', ':'), ensure_ascii=False)
        tenhou6_url_list.append(tenhou6_url)

    with open(output_file, 'w', encoding='utf-8') as f:
        for url in tenhou6_url_list:
            f.write(url + "\n")

if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) != 3:
        print("Usage: python convert.py <input_file> <output_file>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Input file {input_file} does not exist.")
        sys.exit(1)

    convert(input_file, output_file)

