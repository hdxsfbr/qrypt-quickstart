"""Print the shell commands (and short outputs) an agent ran, from a scrubbed codex/claude/cursor stream log."""
import json,sys
for l in open(sys.argv[1]):
    try: e=json.loads(l)
    except: continue
    it=e.get('item') or {}
    if e.get('type')=='item.completed' and it.get('type')=='command_execution':
        print('  $',it.get('command','')[:230].replace('\n',' | '),'=> exit',it.get('exit_code'),'|',(it.get('aggregated_output') or '')[:120].replace('\n',' '))
    if e.get('type')=='assistant':
        for c in e.get('message',{}).get('content',[]):
            if c.get('type')=='tool_use':
                i=c.get('input',{}); print('  T',c.get('name'),str(i.get('command') or i.get('file_path') or i.get('url') or '')[:230].replace('\n',' | '))
    if e.get('type')=='user':
        for c in e.get('message',{}).get('content',[]):
            if isinstance(c,dict) and c.get('type')=='tool_result':
                t=c.get('content'); t=t if isinstance(t,str) else json.dumps(t)
                print('     ->',t[:120].replace('\n',' '))
    if e.get('type')=='tool_call' and e.get('subtype')=='started':
        c=list(e['tool_call'].values())[0].get('args',{}).get('command')
        if c: print('  $',c[:230].replace('\n',' | '))
