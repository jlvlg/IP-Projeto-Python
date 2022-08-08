from random import sample
import csv
import os
import tkinter.filedialog as fd
import colorama
import keyboard

class ExtratorDeProbabilidades:
    def __init__(self, filename):
        self.data = []
        self.filename = filename
        self.length = 0
        self.headers = None
        try: 
            with open(self.filename) as file:
                reader = csv.reader(file)
                self.headers = next(reader)
                self.length = sum(1 for _ in reader)
        except UnicodeDecodeError:
            with open(self.filename, encoding='utf-8') as file:
                reader = csv.reader(file)
                self.headers = next(reader)
                self.length = sum(1 for _ in reader)

    def descarregar(self):
        self.data.clear()

    def carregar_colunas(self, list_colunas, quantidade):
        if quantidade <= 0: 
            return -1
        if not set(list_colunas).issubset(self.headers): 
            return -2
        if quantidade > self.length:
            return -3
        self.actual = list_colunas
        cols = [self.headers.index(col) for col in self.actual]
        lines = sorted(sample(range(self.length), quantidade))
        line_skip = [lines[0]] + [lines[a+1] - lines[a] - 1 for a in range(len(lines)-1)]
        try:
            with open(self.filename) as file:
                self.descarregar()
                reader = csv.reader(file)
                next(reader)
                for x in line_skip:
                    for _ in range(x):
                        next(reader)
                    data = next(reader)
                    self.data.append({self.headers[i]:data[i] for i in cols})
        except UnicodeDecodeError:
            with open(self.filename, encoding='utf-8') as file:
                self.descarregar()
                reader = csv.reader(file)
                next(reader)
                for x in line_skip:
                    for _ in range(x):
                        next(reader)
                    data = next(reader)
                    self.data.append({self.headers[i]:data[i] for i in cols})
        return 0

    def check_num(self, carac):
        for x in self.data:
            if x[carac]:
                try: float(x[carac])
                except ValueError:
                    return -2

    def sample(self, *caracs):
        observed_data = self.data
        for c in caracs:
            if len(c[1]) == 1:
                observed_data = [x for x in observed_data if x[c[0]] == c[1][0]]
            elif len(c[1]) == 2:
                new_data = []
                for x in observed_data:
                    if x[c[0]]:
                        try:
                            if float(c[1][0]) < float(x[c[0]]) < float(c[1][1]):
                                new_data.append(x)
                        except ValueError: return -2
                observed_data = new_data
        return observed_data

    def probabilidade(self, alvo, *caracs):
        observed_data = self.sample(*caracs)
        if observed_data == -2:
            return -2        
        if len(observed_data) == 0:
            return -1
        if len(alvo[1]) == 1:
            return sum(1 for x in observed_data if x[alvo[0]] == alvo[1][0]) / len(observed_data)
        result = 0
        for x in observed_data:
            if x[alvo[0]]:
                try: 
                    if float(alvo[1][0]) < float(x[alvo[0]]) < float(alvo[1][1]):
                        result += 1
                except ValueError:
                    return -2
        return result / len(observed_data)

    def probabilidade_apriori(self, carac, val):
        return self.probabilidade([carac, [val]])

    def probabilidade_apriori_intervalo(self, carac, inicio, fim):
        return self.probabilidade([carac, [inicio, fim]])

    def probabilidade_condicional(self, carac1, val1, carac2, val2):
        return self.probabilidade([carac1, [val1]], [carac2, [val2]])
    
    def probabilidade_condicional_intervalo(self, carac1, val1, carac2, val2):
        return self.probabilidade([carac1, val1], [carac2, val2])
    
    def from_probabilidade(self, probabilidade, alvo, *caracs):
        result = []
        observed_data = [x[alvo[0]] for x in self.sample(*caracs)]
        if len(observed_data) == 0: 
            return -1
        if alvo[1]:
            for x in set(observed_data):
                prob = observed_data.count(x) / len(observed_data)
                if probabilidade >= 0 and prob > probabilidade or probabilidade < 0 and prob < abs(probabilidade):
                        result.append(x)
        else:
            try: observed_data = sorted(float(x) for x in observed_data if x)
            except ValueError: return -2

            if len(observed_data) == 1:
                return (observed_data[0], observed_data[0])
            elif len(observed_data) == 2:
                return tuple(observed_data)

            median = len(observed_data)//2
            min_i = median if probabilidade >= 0 else 0
            max_i = median if probabilidade >= 0 else len(observed_data)-1

            for _ in range(median + 1):
                prob = len([x for x in observed_data if observed_data[min_i] < x < observed_data[max_i]]) / len(observed_data)
                if probabilidade >= 0 and prob > probabilidade or probabilidade < 0 and prob < abs(probabilidade):
                        return (observed_data[min_i], observed_data[max_i])
                min_i = max(0, min_i - 1) if probabilidade >= 0 else min_i + 1
                max_i = min(len(observed_data) - 1, max_i + 1) if probabilidade >= 0 else max_i - 1
        return result

class Menu():
    def __init__(self, title, *options):
        self.title = title
        self.options = options
        
    def execute(self):
        self.selected = 0
        self.__print_menu()
        return self.__listen()

    def __clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def __listen(self):
        keyboard.add_hotkey('up', self.__select_up, suppress=True)
        keyboard.add_hotkey('down', self.__select_down, suppress=True)
        keyboard.wait('enter', suppress=True)
        keyboard.unhook_all()
        return self.__select()

    def __print_menu(self):
        self.__clear()
        padding = max(max(len(y[0]) for y in self.options), len(self.title)) + 2
        title = '\u250c' + '\u2500' * padding + f'\u2510\n\u2502{self.title:^{padding}}\u2502\n\u255E' + '\u2550' * padding + '\u2561'
        content = '\n'.join('\u2502' + ('\033[30;47m' if i == self.selected else '') + f'{x[0]:^{padding}}\033[37;40m\u2502' for i, x in enumerate(self.options))
        ending = '\u2514' + '\u2500' * padding + '\u2518'
        print(title, content, ending, sep='\n')
        # print('\u250C' + '\u2500' * padding + '\u2510')
        # print(f'\u2502{self.title:^{padding}}\u2502')
        # print('\u255E' + '\u2550' * padding + '\u2561')
        # [print(f'\u2502{x[0]:^{padding}}\u2502') for x in self.options[:self.selected]]
        # print('\u2502' + colorama.Fore.BLACK + colorama.Back.WHITE + f'{self.options[self.selected][0]:^{padding}}' + colorama.Style.RESET_ALL + '\u2502')
        # [print(f'\u2502{x[0]:^{padding}}\u2502') for x in self.options[self.selected + 1:]]
        # print('\u2514' + '\u2500' * padding + '\u2518')

    def __select(self):
        if len(self.options[self.selected]) == 2:
            if callable(self.options[self.selected][1][0]):
                if len(self.options[self.selected][1]) == 2:
                    return self.options[self.selected][1][0](*self.options[self.selected][1][1])
                return self.options[self.selected][1][0]()
            return self.options[self.selected][1][0]
        return self.options[self.selected][0]
    
    def __select_up(self):
        self.selected = self.selected - 1 if self.selected > 0 else len(self.options) - 1
        self.__print_menu()

    def __select_down(self):
        self.selected = self.selected + 1 if self.selected < len(self.options) - 1 else 0
        self.__print_menu()

class GUI():
    def __init__(self):
        colorama.init()
        self.__menu_1()
    
    def __exit(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        credits = ('Extrator de Probabilidades',
                   'Projeto desenvolvido e apresentado por José Lucas Vinícius Lopes Gama',
                   'à Universidade Federal do Agreste de Pernambuco como parte dos requisitos',
                   'daa cadeira de Introdução à Programação.',
                   'Orientador: Doutor Luís Filipe Alves Pereira')
        padding = max(len(a) for a in credits)
        print('\u250C' + '\u2500' * (padding + 6) + '\u2510')
        print(f'\u2502   {credits[0]:^{padding}}   \u2502')
        print('\u255E' + '\u2550' * (padding + 6) + '\u2561')
        [print(f'\u2502   {x:<{padding}}   \u2502') for x in credits[1:]]
        print('\u2514' + '\u2500' * (padding + 6) + '\u2518')
        input()
        exit()

    def __print_prob(self, prob):
        match prob:
            case -1:
                print('Probabilidade indefinida, tente selecionar condições menos restritivas')
            case -2:
                print('Coluna selecionada contém valores não numéricos')
            case _: 
                print(f'Probabilidade de {prob:.4f} ou {prob * 100:.2f}%')
        input()

    def __menu_1(self):
        # Eu gosto muito do walrus operator := como você pode perceber
        # Poupa umas várias linhas de código
        while (entrada := Menu('Extrator de Probabilidades', ('Carregar arquivo', (fd.askopenfilename,)), ('Sair', (self.__exit,))).execute()) != 'Sair':
            if entrada:
                self.filename = entrada
                self.file_short = self.filename.split('/')[-1]
                print("Carregando arquivo. Aguarde...")
                self.probabilidade = ExtratorDeProbabilidades(self.filename)
                self.__menu_2()
    
    def __menu_2(self):
        while Menu(f'Carregado: {self.file_short}', ('Carregar colunas', (self.__menu_3,)), ('Escolher outro arquivo', ('menu_1',)), ('Sair', (self.__exit,))).execute() != 'menu_1':
            pass
    
    def __menu_3(self):
        title = 'Selecione as colunas que deseja carregar'
        colunas = set()
        while (entrada := Menu(title, *[[x] for x in self.probabilidade.headers], ('Carregar',), ('Limpar',), ('Cancelar',)).execute()) not in ('Carregar', 'Cancelar'):
            if entrada == 'Limpar':
                colunas.clear()
                title = 'Selecione as colunas que deseja carregar'
            else:
                colunas.add(entrada)
                title = ' '.join(colunas)
        if entrada != 'Cancelar':
            colunas = list(colunas)
            quantidade = None
            while quantidade == None:
                try: quantidade = int(input(f'O arquivo contém {self.probabilidade.length} linhas. Quantas você deseja carregar? '))
                except ValueError: pass
            print('Carregando os dados. Aguarde...', end='\r')
            result = self.probabilidade.carregar_colunas(colunas, quantidade)
            match result:
                case -1:
                    print('Quantidade deve ser maior que 0')
                    input()
                case -2:
                    print('De alguma forma, você foi capaz de selecionar uma coluna indisponível?')
                    input()
                case -3:
                    print('Você selecionou uma quantidade maior que a quantidade de linhas no arquivo')
                    input()
                case 0:
                    self.__menu_4()
    
    def __menu_4(self):
        # Me pergunto quantas linhas usaria se eu tivesse que fazer um menu
        # inteiro toda vez que eu preciso ao invés de usar a classe...
        # Diria que no mínimo três, (:
        while Menu('Selecione uma operação',
            ('Probabilidade a priori', (self.__menu_apriori,)),
            ('Probabilidade a priori intervalo', (self.__menu_intervalo,)),
            ('Probabilidade condicional', (self.__menu_condicional,)),
            ('Probabilidade condicional e intervalo',  (self.__menu_condicional_intervalo,)),
            ('Probabilidade personalizada', (self.__custom_probability,)),
            ('Valor a partir da probabilidade', (self.__from,)),
            ('Descarregar dados', ('menu_2',)),
            ('Sair', (self.__exit,))).execute() != 'menu_2': pass

    def __get_carac(self, title='Selecione a característica'):
        return Menu(title, *[[x] for x in self.probabilidade.actual], ('Cancelar', ('menu_4',))).execute()

    def __get_mul_caracs(self, title):
        t = title
        caracs = set()
        while (entrada := Menu(t, *[[x] for x in self.probabilidade.actual], ('Continuar',), ('Limpar',), ('Cancelar',)).execute()) not in ('Continuar', 'Cancelar'):
            if entrada == 'Limpar':
                caracs.clear()
                t = title
            else:
                caracs.add(entrada)
                t = ' '.join(caracs)
        if entrada != 'Cancelar':
            return list(caracs)
        return 'menu_4'

    def __get_vals(self, caracs):
        vals = [[carac, []] for carac in caracs]
        names = [[carac + ':', [carac]] for carac in caracs]
        title = 'Selecione os valores'
        while (entrada := Menu(title, *names, ('Calcular',), ('Cancelar',)).execute()) != 'Cancelar':
            if entrada == 'Calcular':
                if not all(val[1] or val[1] == '0' for val in vals):
                    title = 'Por favor, selecione um valor para cada característica'
                else:
                    break
            else:
                if (val := self.__range_or_val()) == 'menu_4':
                    return 'menu_4'
                match len(val):
                    case 1:
                        names[caracs.index(entrada)][0] = f'{entrada}: {val[0]}'
                    case 2:
                        if self.probabilidade.check_num(entrada) == -2:
                            self.__print_prob(-2)
                            continue
                        names[caracs.index(entrada)][0] = f'{int(val[0]) if float(val[0]).is_integer() else val[0]} < {entrada} < {int(val[1]) if float(val[1]).is_integer() else val[1]}'
                vals[caracs.index(entrada)][1] = val
        if entrada != 'Cancelar':
            return vals
        return 'menu_4'

    def __get_range(self):
        minimo = 0.0
        maximo = 0.0
        while (entrada := Menu('Selecione o intervalo min < carac < max', (f'Mínimo: {int(minimo) if minimo.is_integer() else minimo}', ('Mínimo',)), (f'Máximo: {int(maximo) if maximo.is_integer() else maximo}', ('Máximo',)), ('Confirmar',), ('Cancelar',)).execute()) not in ('Confirmar', 'Cancelar'):
            try: temp = float(input('Insira o valor do intervalo: '))
            except ValueError: continue
            match entrada:
                case 'Mínimo':
                    minimo = temp
                case 'Máximo':
                    maximo = temp
        if entrada != 'Cancelar':
            return (minimo, maximo)
        return 'menu_4'
    
    def __range_or_val(self, title='Selecione valor ou intervalo'):
        if (entrada := Menu(title, ('Valor',), ('Intervalo', (self.__get_range,)), ('Cancelar', ('menu_4',))).execute()) == 'Valor':
            return [input('Insira o valor: ')]
        return entrada

    def __menu_apriori(self):
        if (caracteristica := self.__get_carac()) != 'menu_4':
            valor = input('Insira o valor desejado: ')
            prob = self.probabilidade.probabilidade_apriori(caracteristica, valor)
            self.__print_prob(prob)
    
    def __menu_intervalo(self):
        if (caracteristica := self.__get_carac()) != 'menu_4' and (intervalo := self.__get_range()) != 'menu_4':
            prob = self.probabilidade.probabilidade_apriori_intervalo(caracteristica, intervalo[0], intervalo[1])
            self.__print_prob(prob)
    
    def __menu_condicional(self):
        if (caracteristica_1 := self.__get_carac('Selecione a característica do alvo')) != 'menu_4':
            valor_1 = input("Insira o valor do alvo: ")
            if (caracteristica_2 := self.__get_carac('Selecione a característica condicional')) != 'menu_4':
                valor_2 = input("Insira o valor da condicional: ")
                prob = self.probabilidade.probabilidade_condicional(caracteristica_1, valor_1, caracteristica_2, valor_2)
                self.__print_prob(prob)
    
    def __menu_condicional_intervalo(self):
        if (caracteristica_1 := self.__get_carac('Selecione a característica do alvo')) != 'menu_4' and (valor_1 := self.__range_or_val()) != 'menu_4':
            if len(valor_1) == 2 and self.probabilidade.check_num(caracteristica_1) == -2:
                print(caracteristica_1)
                self.__print_prob(-2)
                return
            if (caracteristica_2 := self.__get_carac('Selecione a característica condicional')) != 'menu_4' and (valor_2 := self.__range_or_val()) != 'menu_4':
                if len(valor_2) == 2 and self.probabilidade.check_num(caracteristica_2) == -2:
                    self.__print_prob(-2)
                    return
                prob = self.probabilidade.probabilidade_condicional_intervalo(caracteristica_1, valor_1, caracteristica_2, valor_2)
                self.__print_prob(prob)
        
    def __custom(self, t1='Selecione a característica do alvo', t2='Selecione as características condicionais'):
        if (target_carac := self.__get_carac(t1)) != 'menu_4' and (target_val := self.__range_or_val()) != 'menu_4':
            if len(target_val) == 2 and self.probabilidade.check_num(target_carac) == -2:
                print(target_carac)
                self.__print_prob(-2)
                return
            if 'menu_4' not in (caracs := self.__get_mul_caracs(t2)):
                if (vals := self.__get_vals(caracs)) != 'menu_4':
                    return target_carac, target_val, vals
        return 'menu_4'
    
    def __custom_probability(self):
        if (custom := self.__custom()) != 'menu_4':
            target_carac, target_val, vals = custom
            prob = self.probabilidade.probabilidade([target_carac, target_val], *vals)
            self.__print_prob(prob)
    
    def __from(self):
        probabilidade = None
        vals = None
        title = 'Probabilidade personalizada'
        probab = 'Probabilidade:'
        while (entrada := Menu(title, ('Configurar',), (probab, ('Probabilidade',)), ('Calcular',), ('Cancelar',)).execute()) != 'Cancelar':
            match entrada:
                case 'Calcular':
                    if not (vals and probabilidade):
                        title = 'Configure as características e selecione a probabilidade'
                    else:
                        break
                case 'Configurar':
                    if (target_carac := self.__get_carac('Selecione a característica alvo')) != 'menu_4':
                        if (op := Menu('Selecione o resultado esperado', ('Valor', (1,)), ('Intervalo', (0,)), ('Cancelar', ('menu_4',))).execute()) != 'menu_4':
                            if not op and self.probabilidade.check_num(target_carac):
                                self.__print_prob(-2)
                                continue
                            if (caracs := self.__get_mul_caracs('Selecione as características condicionais')) != 'menu_4':
                                if (valores := self.__get_vals(caracs)) != 'menu_4':
                                    vals = valores
                case 'Probabilidade':
                    print('Insira a probabilidade decimal alvo (-1 <= P <= 1):')
                    print('Número positivo: resultado > probabilidade')
                    print('Número negativo: resultado < probabilidade')
                    try: probabilidade = float(input('Insira a probabilidade alvo: '))
                    except ValueError: continue
                    probab = f'Probabilidade: {int(probabilidade) if probabilidade.is_integer() else probabilidade}'
        if entrada != 'Cancelar':
            if len(result := self.probabilidade.from_probabilidade(probabilidade, [target_carac, op], *vals)) == 0:
                print('Não há valores para essa probabilidade e condições')
                input()
                return
            match op:
                case 1:
                    print(f'O(s) valor(es) para {target_carac} que tem a probabilidade condicional {"maior" if probabilidade >= 0 else "menor"} que {probabilidade} é(são):', ', '.join(result))
                case 0:
                    print(f'O intervalo para {target_carac} que tem a probabilidade condicional {"maior" if probabilidade >= 0 else "menor"} que {probabilidade} é: {int(result[0]) if result[0].is_integer() else result[0]} < {target_carac} < {int(result[1]) if result[1].is_integer() else result[1]}')
            input()
            
GUI()
