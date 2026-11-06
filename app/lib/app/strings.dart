import '../core/cards.dart';

/// Everything the app says, in Traditional Chinese (Taiwan).
abstract final class Strings {
  static const appName = '小卡認天下';

  // The card box.
  static const cardBox = '卡片盒';
  static const parent = '家長';
  static const locked = '完整版的卡片';

  // Turning cards over.
  static const home = '回卡片盒';
  static const back = '回去';
  static const next = '下一張';
  static const previous = '上一張';
  static const flipMe = '點一下，翻開卡片';
  static const toCartoon = '換成卡通的圖';
  static const toReal = '換成真的圖';
  static const find = '找找看';

  // Finding.
  static String whereIs(CardItem c) => '${c.zh}在哪裡？';
  static String rightIs(CardItem c) => '對了！是${c.zh}';
  static String thisIs(CardItem c) => '這是${c.zh}喔';
  static String tryAgain(CardItem wrong, CardItem target) => '這是${wrong.zh}喔，再找找${target.zh}';
  static const allFound = '好棒！都找到了！';
  static const again = '再找一次';
  static const backToCards = '回去翻卡片';

  // Resting.
  static const restTitle = '休息一下';
  static String restLine(CardItem c) => c.deck == 'body' ? '眼睛休息一下，\n我們去摸摸自己的${c.zh}吧！' : '眼睛休息一下，\n我們去找找家裡的${c.zh}吧！';

  // Parent gate (as in the sibling apps).
  static const callParent = '請爸爸媽媽來幫忙喔！';
  static const parentGateTitle = '家長確認';
  static String gateQuestion(String a, String b) => '$a 加 $b 等於多少？';
  static const gateRules = '答錯三次要等一分鐘。';
  static const wrongAnswer = '不對喔，換一題。';
  static String gateWait(int s) => '請等 $s 秒再試';
  static const backspace = '刪掉';
  static const cancel = '取消';

  // Parent mode.
  static const parentTitle = '家長模式';
  static const playTime = '每次可以玩多久';
  static String minutes(int m) => '$m 分鐘';
  static const playTimeNote = '時間到了，畫面會溫柔地請小朋友休息，並請他去找找家裡剛剛看過的東西。國民健康署建議：未滿 2 歲避免看螢幕；2 歲以上每天不超過 1 小時，每 30 分鐘休息一下。';
  static const playOn = '讓小朋友再玩一次（重新計時）';
  static const resting = '現在是休息時間。';
  static const cardsSection = '卡片';
  static const firstPicture = '一開始看到的圖';
  static const realPicture = '真實版（像真的東西，建議）';
  static const cartoonPicture = '卡通版';
  static const pictureNote = '小朋友看卡片時，可以點右上角自己切換。';
  static const english = '名字後面加英文（dog）';
  static const choices = '找找看：幾張卡片裡找';
  static String cards(int n) => '$n 張';
  static const sound = '聲音';
  static const music = '背景音樂';
  static const effects = '音效和動物的叫聲';
  static const voice = '念出名字';
  static const progress = '玩過的卡片';
  static String deckLine(int seen, int known, int total) => '翻過 $seen／$total 張，認得 $known 張';
  static const knownNote = '「認得」：在找找看找對三次以上。';
  static const together = '一起玩的小提示';
  static const tips = [
    '洗澡的時候，一起說身體的名字：「眼睛在哪裡？」',
    '吃水果的時候問：「這是什麼？什麼顏色？」',
    '出門的時候，一起找找公車、機車、腳踏車。',
    '穿衣服的時候說：「先穿襪子，再穿鞋子。」',
    '小朋友說錯也沒關係，笑著說一次正確的名字就好。',
  ];
  static const fullVersion = '完整版';
  static const fullNote = '免費版有動物和水果兩組；完整版有全部的卡片。（測試版先全部打開。）';
  static const fullSwitch = '打開完整版（測試用）';
  static const about = '關於';
  static const privacy = '不連網、不定位、沒有廣告、沒有帳號；玩的紀錄不會傳給任何人，只存在這支手機（和家長自己帳號的手機備份）裡。';
  static String version(String v) => '版本 $v';
}
