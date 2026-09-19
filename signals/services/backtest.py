from dataclasses import dataclass
from .strategy import analyse

@dataclass
class BacktestResult:
    trades:list; metrics:dict

def run_backtest(frame,fee_rate=0.001,slippage=0.0005,warmup=210):
    trades=[]
    for i in range(warmup,len(frame)-1):
        d=analyse(frame.iloc[:i+1])
        if d.status!="confirmed": continue
        entry=float(d.levels["entry_high"])*(1+slippage); stop=float(d.levels["stop_loss"]); target=float(d.levels["target_2"]); result=None; exit_price=None
        expiry=d.levels["expires_at"]
        for _,bar in frame.iloc[i+1:].iterrows():
            if bar.open_time>expiry: result="expired"; exit_price=float(bar.close); break
            hit_stop=float(bar.low)<=stop; hit_target=float(bar.high)>=target
            if hit_stop and hit_target: result="stopped"; exit_price=stop; break
            if hit_stop: result="stopped"; exit_price=stop; break
            if hit_target: result="won"; exit_price=target; break
        if result:
            r=((exit_price*(1-fee_rate))/(entry*(1+fee_rate))-1)/((entry-stop)/entry)
            trades.append({"entry_time":str(frame.iloc[i+1].open_time),"entry":entry,"exit":exit_price,"result":result,"r":r})
    rs=[t["r"] for t in trades]; wins=[r for r in rs if r>0]; losses=[r for r in rs if r<=0]
    metrics={"signals":len(trades),"win_rate":len(wins)/len(rs) if rs else 0,"expectancy_r":sum(rs)/len(rs) if rs else 0,"profit_factor":sum(wins)/abs(sum(losses)) if losses and sum(losses) else None}
    return BacktestResult(trades,metrics)
