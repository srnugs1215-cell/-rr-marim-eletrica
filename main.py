# -*- coding: utf-8 -*-
"""Aplicativo offline RR Marim Elétrica - interface Android Kivy."""
import json, os, re
from datetime import date
from pathlib import Path

from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

import dimensionador as de

Window.clearcolor = (0.055, 0.09, 0.15, 1)


def parse_num(value, default=0.0):
    try:
        return float(str(value).strip().replace(',', '.'))
    except Exception:
        return float(default)


def safe_name(s):
    return de.slug(s) or 'dimensionamento'

class RRMarimApp(App):
    def build(self):
        self.title = 'RR Marim Elétrica'
        self.data_dir = Path(self.user_data_dir)
        self.projects_dir = self.data_dir / 'projetos'
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        de.PASTA = self.projects_dir
        self.comodos = []
        self.tues = []
        self._make_ui()
        return self.root

    def _make_ui(self):
        outer = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(72), spacing=dp(2))
        header.add_widget(Label(text='RR MARIM ELÉTRICA', bold=True, font_size='22sp', color=(0.96,0.97,1,1)))
        header.add_widget(Label(text='DIMENSIONADOR ELÉTRICO • OFFLINE', font_size='12sp', color=(0.55,0.78,1,1)))
        outer.add_widget(header)
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))
        self.body = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10), padding=(0,0,0,dp(20)))
        self.body.bind(minimum_height=self.body.setter('height'))
        scroll.add_widget(self.body)
        outer.add_widget(scroll)
        self.root = outer
        self._section('Dados do projeto')
        self.proj_nome = self._field('Nome do projeto *', 'Ex.: Casa do cliente')
        self.cliente = self._field('Cliente', '')
        self.local = self._field('Endereço / local', '')
        self.sistema = self._spinner('Sistema de tensão', ['127/220 V', '220/380 V'], '127/220 V')
        self.fornecimento = self._spinner('Fornecimento', ['Monofásico (F+N)', 'Bifásico (2F+N)', 'Trifásico (3F+N)'], 'Bifásico (2F+N)')
        self.dist_medidor = self._field('Distância medidor → quadro (m)', '10')
        self.queda_circ = self._field('Queda máxima dos circuitos (%)', '3')
        self.queda_alim = self._field('Queda máxima do alimentador (%)', '2')
        self.circ_eletroduto = self._field('Circuitos por eletroduto', '3')
        self.demanda = self._spinner('Aplicar fator de demanda?', ['Sim', 'Não'], 'Sim')

        self._section('Adicionar cômodo')
        self.tipo_comodo = self._spinner('Tipo de cômodo', [v['nome'] for v in de.TIPOS.values()], 'Sala')
        self.comodo_nome = self._field('Nome do cômodo', 'Sala')
        self.area = self._field('Área (m²)', '12')
        self.perimetro = self._field('Perímetro (m)', '14')
        self.dist_comodo = self._field('Distância quadro → cômodo (m)', '10')
        self.ilum = self._field('Iluminação (VA)', '160')
        self.tug = self._field('Quantidade de tomadas TUG', '4')
        self._button('Adicionar cômodo', self.add_comodo, (0.12,0.48,0.72,1))
        self.comodos_label = self._info('Nenhum cômodo adicionado.')

        self._section('Adicionar carga específica (TUE)')
        self.tue_nome = self._field('Equipamento', 'Chuveiro')
        self.tue_pot = self._field('Potência (W)', '5500')
        self.tue_modo = self._spinner('Ligação', ['Fase + neutro', 'Fase + fase', 'Trifásico'], 'Fase + neutro')
        self.tue_fp = self._field('Fator de potência', '1')
        self.tue_qtd = self._field('Quantidade', '1')
        self.tue_dist = self._field('Distância quadro → carga (m)', '10')
        self.tue_molhada = self._spinner('Área molhada?', ['Não', 'Sim'], 'Não')
        self._button('Adicionar carga TUE', self.add_tue, (0.12,0.48,0.72,1))
        self.tues_label = self._info('Nenhuma carga TUE adicionada.')

        self._section('Calcular e gerar relatório')
        self._button('CALCULAR DIMENSIONAMENTO', self.calculate, (0.05,0.62,0.36,1), height=dp(52))
        self._button('GERAR PDF E SALVAR PROJETO', self.generate_pdf, (0.08,0.52,0.34,1), height=dp(48))
        self._button('Ver projetos salvos', self.list_projects, (0.25,0.30,0.40,1))
        self.result_label = self._info('Preencha os dados, adicione ao menos um cômodo e toque em CALCULAR.', font_size='14sp')
        self.last_proj = None
        self.last_res = None

    def _section(self, text):
        lab = Label(text=text, bold=True, font_size='17sp', color=(0.42,0.75,1,1), size_hint_y=None, height=dp(32), halign='left', valign='middle')
        lab.bind(size=lambda w, s: setattr(w, 'text_size', s))
        self.body.add_widget(lab)
        line = Label(text='━━━━━━━━━━━━━━━━━━━━━━━━━━━━', color=(0.2,0.36,0.5,1), size_hint_y=None, height=dp(12), font_size='10sp')
        self.body.add_widget(line)

    def _field(self, label, default=''):
        box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(68), spacing=dp(3))
        box.add_widget(Label(text=label, font_size='13sp', color=(0.86,0.9,0.96,1), size_hint_y=None, height=dp(23), halign='left', valign='middle', text_size=(Window.width-dp(30),None)))
        inp = TextInput(text=default, multiline=False, size_hint_y=None, height=dp(42), font_size='16sp', padding=(dp(10),dp(9)), background_color=(0.12,0.17,0.24,1), foreground_color=(1,1,1,1), cursor_color=(0.4,0.75,1,1))
        box.add_widget(inp)
        self.body.add_widget(box)
        return inp

    def _spinner(self, label, values, default):
        box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(68), spacing=dp(3))
        box.add_widget(Label(text=label, font_size='13sp', color=(0.86,0.9,0.96,1), size_hint_y=None, height=dp(23), halign='left', valign='middle', text_size=(Window.width-dp(30),None)))
        sp = Spinner(text=default, values=values, size_hint_y=None, height=dp(42), font_size='15sp', background_color=(0.12,0.26,0.39,1), color=(1,1,1,1))
        box.add_widget(sp)
        self.body.add_widget(box)
        return sp

    def _button(self, text, callback, color, height=None):
        btn = Button(text=text, size_hint_y=None, height=height or dp(46), background_normal='', background_color=color, color=(1,1,1,1), bold=True, font_size='14sp')
        btn.bind(on_release=lambda *_: callback())
        self.body.add_widget(btn)
        return btn

    def _info(self, text, font_size='13sp'):
        lab = Label(text=text, markup=True, font_size=font_size, color=(0.87,0.91,0.97,1), size_hint_y=None, height=dp(70), halign='left', valign='top')
        lab.bind(width=lambda w, val: setattr(w, 'text_size', (val, None)), texture_size=lambda w, val: setattr(w, 'height', max(dp(45), val[1]+dp(10))))
        self.body.add_widget(lab)
        return lab

    def popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        lbl = Label(text=message, color=(0.08,0.1,0.14,1), halign='left', valign='middle')
        lbl.bind(size=lambda w,s: setattr(w,'text_size',s))
        content.add_widget(lbl)
        b = Button(text='OK', size_hint_y=None, height=dp(44))
        content.add_widget(b)
        p = Popup(title=title, content=content, size_hint=(.9,.55), auto_dismiss=False)
        b.bind(on_release=p.dismiss)
        p.open()

    def add_comodo(self):
        try:
            nome = self.comodo_nome.text.strip() or self.tipo_comodo.text
            tipo = next(k for k,v in de.TIPOS.items() if v['nome'] == self.tipo_comodo.text)
            area = parse_num(self.area.text)
            per = parse_num(self.perimetro.text)
            dist = parse_num(self.dist_comodo.text)
            if area <= 0 or per < 0 or dist < 0: raise ValueError('Área deve ser maior que zero; distâncias não podem ser negativas.')
            tq = max(0, int(parse_num(self.tug.text)))
            il = max(0, parse_num(self.ilum.text))
            self.comodos.append(dict(tipo=tipo, nome=nome, area=area, perim=per, dist=dist, ilum_va=il, tug_qtd=tq, tug_va=de.tug_va(de.TIPOS[tipo], tq)))
            self.comodos_label.text = '\n'.join(f'• {c["nome"]}: {c["area"]:g} m² | iluminação {c["ilum_va"]:g} VA | {c["tug_qtd"]} TUG' for c in self.comodos)
            self.comodos_label.height = dp(35 + 22*len(self.comodos))
            self.comodo_nome.text = ''; self.area.text='12'; self.perimetro.text='14'; self.dist_comodo.text='10'
            self.popup('Cômodo adicionado', f'{nome} foi adicionado ao projeto.')
        except Exception as e: self.popup('Verifique os dados', str(e))

    def add_tue(self):
        try:
            nome = self.tue_nome.text.strip()
            pot = parse_num(self.tue_pot.text)
            fp = parse_num(self.tue_fp.text,1)
            qtd = int(parse_num(self.tue_qtd.text,1))
            dist = parse_num(self.tue_dist.text)
            if not nome or pot <= 0 or not .3 <= fp <= 1 or qtd < 1 or dist < 0: raise ValueError('Confira nome, potência, FP (0,3 a 1), quantidade e distância.')
            modo = {'Fase + neutro':'fn','Fase + fase':'ff','Trifásico':'tri'}[self.tue_modo.text]
            if modo == 'ff' and self.fornecimento.text.startswith('Monofásico'): raise ValueError('A ligação fase + fase precisa de fornecimento bifásico ou trifásico.')
            if modo == 'tri' and not self.fornecimento.text.startswith('Trifásico'): raise ValueError('A ligação trifásica precisa de fornecimento trifásico.')
            self.tues.append(dict(nome=nome,pot_w=pot,modo=modo,fp=fp,qtd=qtd,dist=dist,molhada=self.tue_molhada.text=='Sim'))
            self.tues_label.text = '\n'.join(f'• {t["nome"]}: {t["pot_w"]:g} W × {t["qtd"]} | {de.MODO_TXT[t["modo"]]}' for t in self.tues)
            self.tues_label.height = dp(35 + 22*len(self.tues))
            self.popup('Carga adicionada', f'{nome} foi adicionado ao projeto.')
        except Exception as e: self.popup('Verifique os dados', str(e))

    def make_project(self):
        if not self.proj_nome.text.strip(): raise ValueError('Informe o nome do projeto.')
        if not self.comodos: raise ValueError('Adicione pelo menos um cômodo.')
        vf, vl = (127,220) if self.sistema.text.startswith('127') else (220,380)
        nf = {'Monofásico (F+N)':1,'Bifásico (2F+N)':2,'Trifásico (3F+N)':3}[self.fornecimento.text]
        par = dict(vf=vf,vl=vl,nfases=nf,queda_circ=parse_num(self.queda_circ.text,3),queda_alim=parse_num(self.queda_alim.text,2),circ_por_eletroduto=max(1,int(parse_num(self.circ_eletroduto.text,3))),aplicar_fd=self.demanda.text=='Sim',dist_medidor=parse_num(self.dist_medidor.text,10))
        if not 0.5 <= par['queda_circ'] <= 4 or not .2 <= par['queda_alim'] <= 4: raise ValueError('Confira os limites de queda de tensão (circuitos 0,5–4%; alimentador 0,2–4%).')
        return dict(nome=self.proj_nome.text.strip(),cliente=self.cliente.text.strip(),local=self.local.text.strip(),data=date.today().strftime('%d/%m/%Y'),params=par,comodos=self.comodos,tues=self.tues)

    def calculate(self):
        try:
            proj = self.make_project(); res = de.calcular(proj)
            self.last_proj, self.last_res = proj, res
            al = res['alim']
            lines = [f'[b]RESUMO DO DIMENSIONAMENTO[/b]',f'Cômodos: {len(proj["comodos"])} | Cargas TUE: {len(proj["tues"])}',f'C circuitos: {len(res["circuitos"])}',f'Carga instalada: {res["total_inst"]:.0f} VA',f'Demanda calculada: {res["dem"]:.0f} VA',f'Corrente de demanda: {de.fmt(al["i_dem"])} A',f'Disjuntor geral: {al["in_a"]} A | alimentador: {de.fmt_s(al["secao"])} mm²','', '[b]CIRCUITOS[/b]']
            for c in res['circuitos']:
                lines.append(f'{c["num"]}. {c["nome"]} — {c["in_a"]} A | cabo {de.fmt_s(c["secao"])} mm² | DR: {"Sim" if c["dr"] else "Não"}')
            if res['avisos']:
                lines += ['', '[b]ATENÇÃO[/b]'] + [f'• {a}' for a in res['avisos']]
            lines += ['', 'IMPORTANTE: conferir os resultados e as condições reais da instalação antes de executar.']
            self.result_label.text='\n'.join(lines)
            self.result_label.height=dp(60+23*len(lines))
            self.popup('Cálculo concluído','Resultados exibidos abaixo. Confira os avisos técnicos antes de usar o dimensionamento.')
        except Exception as e: self.popup('Não foi possível calcular', str(e))

    def generate_pdf(self):
        try:
            if self.last_proj is None or self.last_res is None:
                self.calculate()
                if self.last_proj is None: return
            base = safe_name(self.last_proj['nome'])
            json_path = self.projects_dir / f'{base}.json'
            pdf_path = self.projects_dir / f'{base}.pdf'
            json_path.write_text(json.dumps(self.last_proj, ensure_ascii=False, indent=2), encoding='utf-8')
            de.gerar_pdf(self.last_proj, self.last_res, pdf_path)
            self.popup('PDF gerado', f'Relatório salvo no armazenamento do aplicativo:\n{pdf_path}\n\nO projeto também foi salvo para reabrir depois. Use “Ver projetos salvos” para consultar os arquivos.')
        except Exception as e: self.popup('Erro ao gerar PDF', str(e))

    def list_projects(self):
        files = sorted(self.projects_dir.glob('*.json'))
        if not files:
            self.popup('Projetos salvos','Ainda não há projetos salvos. Calcule e gere o PDF de um projeto primeiro.')
            return
        msg = '\n\n'.join(f.stem for f in files[-20:])
        self.popup('Projetos salvos (mais recentes)',msg)

if __name__ == '__main__':
    RRMarimApp().run()
