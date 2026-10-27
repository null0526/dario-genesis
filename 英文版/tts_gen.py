"""逐句生成英文旁白：tts_lines.tsv 的每一行 -> tts/<引擎>-<音色>/<id>.mp3|wav。
每句旁边存 <id>.txt 记下生成时的读法；音频存在且读法没变才跳过，改了译稿的句子会自动重新生成。

用法：
    python tts_gen.py polly Matthew [--until 33]       # Amazon Polly 生成式音色
    python tts_gen.py minimax English_expressive_narrator [--until 33]   # MiniMax Speech 2.8 HD（官方接口）
    python tts_gen.py openrouter <音色> [--until 33]    # 经 OpenRouter 调 minimax/speech-2.8-hd（原片的请求格式）
    python tts_gen.py kokoro bm_george [--until 33]    # 本地 Kokoro-82M，不花钱
    python tts_gen.py minimax --list                   # 列出可用音色（polly 同理）
--until 秒：只生成起点早于这个时间（原成片时间）的句子，用来出试听样片。

需要的环境变量（在环境设置里加，开新会话后生效）：
    Polly：POLLY_ACCESS_KEY_ID、POLLY_SECRET_ACCESS_KEY，可选 POLLY_REGION（默认 us-east-1）
    MiniMax：MINIMAX_API_KEY，可选 MINIMAX_API_HOST（默认 api.minimax.io，国内账号用 api.minimaxi.com）
    OpenRouter：OPENROUTER_API_KEY"""
import argparse, csv, json, os, re, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))


def rows(until=None):
    rs = list(csv.DictReader(open(os.path.join(HERE, 'tts_lines.tsv'), encoding='utf-8'), delimiter='\t'))
    return [r for r in rs if until is None or float(r['start']) < until]


def post(url, body, headers):
    req = urllib.request.Request(url, json.dumps(body).encode(), {'Content-Type': 'application/json', **headers})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def polly_client():
    import boto3
    return boto3.client('polly', region_name=os.environ.get('POLLY_REGION', 'us-east-1'),
                        aws_access_key_id=os.environ['POLLY_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['POLLY_SECRET_ACCESS_KEY'])


def polly(text, voice, _cache={}):
    c = _cache.setdefault('c', polly_client())
    r = c.synthesize_speech(Engine='generative', VoiceId=voice, OutputFormat='mp3', SampleRate='24000', Text=text)
    return r['AudioStream'].read(), 'mp3'


def minimax(text, voice):
    host = os.environ.get('MINIMAX_API_HOST', 'api.minimax.io')
    d = json.loads(post(f'https://{host}/v1/t2a_v2', {
        'model': 'speech-2.8-hd', 'text': text, 'stream': False,
        'voice_setting': {'voice_id': voice, 'speed': 1.0, 'vol': 1.0, 'pitch': 0},
        'audio_setting': {'sample_rate': 32000, 'bitrate': 128000, 'format': 'mp3', 'channel': 1}},
        {'Authorization': 'Bearer ' + os.environ['MINIMAX_API_KEY']}))
    assert d.get('base_resp', {}).get('status_code') == 0, d.get('base_resp')
    return bytes.fromhex(d['data']['audio']), 'mp3'


def openrouter(text, voice):
    return post('https://openrouter.ai/api/v1/audio/speech',
                {'model': 'minimax/speech-2.8-hd', 'input': text, 'voice': voice, 'response_format': 'mp3'},
                {'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY']}), 'mp3'


def kokoro(text, voice, _cache={}):
    """kokoro-onnx。KOKORO_DIR（默认 英文版/kokoro/）里放 model.onnx 和各音色的 <音色>.bin，
    均取自 huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX（onnx/model.onnx、voices/*.bin）。"""
    import glob, io, numpy as np, soundfile
    from kokoro_onnx import Kokoro
    if 'k' not in _cache:
        d = os.environ.get('KOKORO_DIR', os.path.join(HERE, 'kokoro')); npz = os.path.join(d, 'voices.npz')
        np.savez(npz, **{os.path.basename(f)[:-4]: np.fromfile(f, '<f4').reshape(-1, 1, 256) for f in glob.glob(os.path.join(d, '*.bin'))})
        _cache['k'] = Kokoro(os.path.join(d, 'model.onnx'), npz)
    lang = 'en-gb' if voice[0] == 'b' else 'en-us'
    if any(w in text for w in PHONEMES):     # 人名等 espeak 读不对的词：分段转音标，再拼上指定读音
        parts = re.split('(' + '|'.join(map(re.escape, PHONEMES)) + ')', text)
        ph = ' '.join(PHONEMES.get(p) or _cache['k'].tokenizer.phonemize(p, lang) for p in parts if p.strip())
        audio, sr = _cache['k'].create(ph, voice=voice, speed=1.0, is_phonemes=True)
    else:
        audio, sr = _cache['k'].create(text, voice=voice, speed=1.0, lang=lang)
    buf = io.BytesIO(); soundfile.write(buf, audio, sr, format='WAV'); return buf.getvalue(), 'wav'


PHONEMES = {'Amodei': 'ɑːmˈoʊdeɪ', 'Zu Chongzhi': 'dzˈuː tʃˌʊŋdʒˈɜː'}   # Kokoro 专用读音


def list_voices(engine):
    if engine == 'polly':
        for v in polly_client().describe_voices(Engine='generative')['Voices']:
            if v['LanguageCode'].startswith('en'): print(v['LanguageCode'], v['Id'], v['Gender'])
    elif engine == 'minimax':
        host = os.environ.get('MINIMAX_API_HOST', 'api.minimax.io')
        d = json.loads(post(f'https://{host}/v1/get_voice', {'voice_type': 'system'}, {'Authorization': 'Bearer ' + os.environ['MINIMAX_API_KEY']}))
        for v in d.get('system_voice', []):
            if v['voice_id'].lower().startswith('english'): print(v['voice_id'], '|', ' '.join(v.get('description') or []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('engine', choices=['polly', 'minimax', 'openrouter', 'kokoro'])
    ap.add_argument('voice', nargs='?'); ap.add_argument('--until', type=float); ap.add_argument('--list', action='store_true')
    a = ap.parse_args()
    if a.list: return list_voices(a.engine)
    out = os.path.join(HERE, 'tts', f'{a.engine}-{a.voice}'); os.makedirs(out, exist_ok=True)
    fn = globals()[a.engine]; chars = 0
    for r in rows(a.until):
        audio = [os.path.join(out, f"{r['id']}.{e}") for e in ('mp3', 'wav')]
        side = os.path.join(out, f"{r['id']}.txt")
        if any(map(os.path.exists, audio)) and os.path.exists(side) and open(side, encoding='utf-8').read() == r['text']: continue
        for f in audio:
            if os.path.exists(f): os.remove(f)       # 读法变了或没有记录：旧音频作废
        data, ext = fn(r['text'], a.voice); chars += len(r['text'])
        open(os.path.join(out, f"{r['id']}.{ext}"), 'wb').write(data)
        open(side, 'w', encoding='utf-8').write(r['text'])
        print(r['id'], len(data), 'bytes', flush=True)
    print(f'done -> {out}，本次 {chars} 字符')


if __name__ == '__main__':
    main()
