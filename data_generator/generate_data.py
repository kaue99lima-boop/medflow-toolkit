"""Gerador de dados 100% fictícios para o MedFlow Toolkit.
Uso: python generate_data.py [pasta_saida]   (padrão: ../data)
Semente fixa: mesma saída sempre. Nenhum dado real."""
import csv, io, os, random, sys, datetime as dt

SEED = 42
PAYERS = ['Seguradora Alfa', 'Seguradora Beta', 'Seguradora Gama', 'Seguradora Delta', 'Seguradora Épsilon', 'Particular']
LINES = ['Urgência', 'Cirurgia', 'Internação', 'Imagem', 'Laboratório']
DOCTORS = [('D01', 'Dr. Álvaro Demo', 'Cirurgia Geral'), ('D02', 'Dra. Beatriz Teste', 'Ortopedia'), ('D03', 'Dr. Caio Exemplo', 'Urologia'),
           ('D04', 'Dra. Diana Modelo', 'Ginecologia'), ('D05', 'Dr. Enzo Amostra', 'Cirurgia Geral'), ('D06', 'Dra. Fabiana Ficção', 'Otorrino'),
           ('D07', 'Dr. Gael Sintético', 'Ortopedia'), ('D08', 'Dra. Helena Padrão', 'Cirurgia Plástica')]
SUPPLIERS = ['Fornecedor A', 'Fornecedor B', 'Fornecedor C', 'Fornecedor D', 'Fornecedor E', 'Fornecedor F']
WAREHOUSES = ['Farmácia', 'Almoxarifado', 'Central']
CATS = {'Descartáveis': ['Luva cirúrgica', 'Seringa 10 ml', 'Agulha 25x7', 'Gaze estéril', 'Cateter venoso', 'Equipo simples', 'Máscara cirúrgica', 'Campo cirúrgico', 'Sonda vesical', 'Atadura crepom'],
        'Medicamentos': ['Analgésico injetável', 'Antibiótico profilático', 'Anestésico local', 'Soro fisiológico 500 ml', 'Antiemético', 'Anti-inflamatório', 'Heparina', 'Sedativo curto', 'Solução ringer', 'Antisséptico'],
        'Implantes': ['Tela de hérnia', 'Parafuso ortopédico', 'Placa de fixação', 'Sutura mecânica', 'Clipe cirúrgico', 'Dreno tubular'],
        'Serviços': ['Sala cirúrgica (hora)', 'Diária de apartamento', 'Taxa de esterilização', 'Honorário de anestesia', 'Exame pré-operatório']}


def csv_text(cols, rows):
    s = io.StringIO(); w = csv.writer(s, lineterminator='\n'); w.writerow(cols); w.writerows(rows); return s.getvalue()


def gen_all():
    r = random.Random(SEED); out = {}
    end = dt.date(2026, 10, 12)
    # billing
    rows = []
    for i in range(1, 1101):
        d = end - dt.timedelta(days=r.randint(0, 200))
        payer = r.choices(PAYERS, [18, 16, 14, 12, 8, 14])[0]
        line = r.choices(LINES, [34, 12, 14, 20, 20])[0]
        base = {'Urgência': 120, 'Cirurgia': 2400, 'Internação': 1700, 'Imagem': 160, 'Laboratório': 45}[line]
        amt = round(base * r.uniform(0.6, 1.6), 2)
        age = (end - d).days
        st = 'paga' if (payer == 'Particular' and r.random() < .6) or r.random() < max(.1, .85 - age / 120) else ('rejeitada' if r.random() < .12 else 'em aberto')
        rows.append([f'AC{100000+i}', f'P{r.randint(1000,9999)}', d.isoformat(), payer, line, amt, st])
    rows.sort(key=lambda x: x[2]); out['billing.csv'] = csv_text(['account_id', 'patient_code', 'service_date', 'payer', 'service_line', 'amount', 'status'], rows)
    # catalog / packages
    cat, i = [], 1
    for c, names in CATS.items():
        for n in names:
            cost = round({'Descartáveis': 4, 'Medicamentos': 12, 'Implantes': 380, 'Serviços': 220}[c] * r.uniform(.4, 2.2), 2)
            cat.append([f'IT{i:03d}', c, n, cost]); i += 1
    out['catalog.csv'] = csv_text(['item_id', 'category', 'description', 'unit_cost'], cat)
    pk = []
    pnames = ['Colecistectomia videolaparoscópica', 'Hernioplastia inguinal', 'Artroscopia de joelho', 'Ressecção endoscópica de próstata', 'Histerectomia', 'Septoplastia']
    for k, pn in enumerate(pnames, 1):
        chosen = r.sample(cat, 8)
        for it in chosen:
            q = r.choice([1, 1, 2, 4, 10]) if it[1] in ('Descartáveis', 'Medicamentos') else 1
            pk.append([f'PK{k:02d}', pn, it[0], q])
    out['packages.csv'] = csv_text(['package_id', 'package_name', 'item_id', 'qty'], pk)
    out['doctors.csv'] = csv_text(['doctor_id', 'doctor_name', 'specialty'], DOCTORS)
    # stock + consumption
    stock, cons = [], []
    items = [(c, n) for c, ns in CATS.items() if c != 'Serviços' for n in ns] + [('Descartáveis', f'Insumo genérico {k}') for k in range(1, 39)]
    for k, (c, n) in enumerate(items, 1):
        sku = f'SKU{k:03d}'; daily = r.choice([0.3, 0.8, 2, 5, 12]) * r.uniform(.6, 1.4)
        lead = r.choice([3, 5, 7, 10, 15]); cover = r.choice([1, 3, 6, 12, 25, 40, 60, 110, 200])
        qty = max(0, round(daily * cover * r.uniform(.8, 1.2)))
        cost = round({'Descartáveis': 3, 'Medicamentos': 9, 'Implantes': 300}[c] * r.uniform(.4, 2.5), 2)
        abc = 'A' if cost * daily > 40 else ('B' if cost * daily > 8 else 'C')
        exp = end + dt.timedelta(days=r.choice([12, 25, 40, 90, 180, 365, 540]))
        stock.append([sku, n, abc, r.choice(WAREHOUSES), qty, cost, r.choice(SUPPLIERS), lead, exp.isoformat()])
        for d in range(90):
            day = end - dt.timedelta(days=89 - d)
            q = max(0, round(r.gauss(daily, daily * .5)))
            if q: cons.append([day.isoformat(), sku, q])
    out['stock.csv'] = csv_text(['sku', 'description', 'abc_class', 'warehouse', 'stock_qty', 'unit_cost', 'supplier', 'lead_time_days', 'expiry_date'], stock)
    out['consumption.csv'] = csv_text(['date', 'sku', 'qty'], cons)
    # P&L (monthly; last month partial)
    pl = []
    lines_fixed = [('Folha direta', 70000), ('Folha administrativa', 52000), ('Serviços terceiros', 42000), ('Manutenção', 15000), ('Aluguel', 11000), ('Utilidades', 9000), ('Outros', 14000)]
    rev = 230000
    for m in range(1, 11):
        rev *= r.uniform(.96, 1.16)
        partial = (m == 10); f = 12 / 31 if partial else 1; de = 12 if partial else ''
        pl.append([f'2026-{m:02d}', 'Receita', 'receita', round(rev * f), de])
        pl.append([f'2026-{m:02d}', 'Materiais e medicamentos', 'variavel', round(rev * .12 * r.uniform(.9, 1.1) * f), de])
        pl.append([f'2026-{m:02d}', 'Serviços terceiros variáveis', 'variavel', round(rev * .06 * r.uniform(.85, 1.15) * f), de])
        for n, v in lines_fixed:
            pl.append([f'2026-{m:02d}', n, 'fixo', round(v * r.uniform(.96, 1.05) * f), de])
    out['pl.csv'] = csv_text(['month', 'line', 'kind', 'amount', 'days_elapsed'], pl)
    # doctor payments
    pay, n = [], 1
    procs = ['Colecistectomia', 'Hernioplastia', 'Artroscopia', 'Ressecção endoscópica', 'Histerectomia', 'Septoplastia', 'Consulta de urgência', 'Avaliação cirúrgica']
    for did, name, sp in DOCTORS:
        for m in range(1, 11):
            for _ in range(r.randint(8, 20)):
                d = dt.date(2026, m, r.randint(1, 28)); amt = round(r.choice([120, 180, 450, 700, 900, 1400]) * r.uniform(.8, 1.2), 2)
                ap = (m < 10 and r.random() > .08) or (m == 10 and r.random() > .6)
                pd_ = (d + dt.timedelta(days=r.randint(25, 50))).isoformat() if ap else ''
                pay.append([f'PG{n:05d}', name, d.isoformat(), r.choice(procs), f'P{r.randint(1000,9999)}', amt, 'aprovado' if ap else 'pendente', pd_]); n += 1
    out['doctor_payments.csv'] = csv_text(['payment_id', 'doctor_name', 'procedure_date', 'procedure', 'patient_code', 'amount', 'status', 'payment_date'], pay)
    return out


if __name__ == '__main__':
    folder = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(folder, exist_ok=True)
    for name, text in gen_all().items():
        open(os.path.join(folder, name), 'w', encoding='utf-8').write(text)
    print('Dados fictícios gerados em', os.path.abspath(folder))
