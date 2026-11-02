
from datetime import date, datetime
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


# Repositorio que armazena os banners
REPOSITORIO = (
    "https://raw.githubusercontent.com/"
    "d-ribeiro-dev/calendario-vivo-github/main"
)

# Datas e caminhos das imagens cadastradas
CELEBRACOES = {
    (10, 31): {
        "nome": "Halloween",
        "imagem": "banners/halloween/halloween-animation.gif",
    },
    (11, 2): {
        "nome": "Dia de Finados",
        "imagem": "banners/finados/finados.png",
    },
}

# Marcadores da area automatica do README
INICIO = "<!-- CALENDARIO-VIVO:INICIO -->"
FIM = "<!-- CALENDARIO-VIVO:FIM -->"


def verificar_imagem(url):
    """Confere se a imagem esta acessivel no repositorio."""

    requisicao = Request(
        url,
        headers={"User-Agent": "Calendario-Vivo"}
    )

    with urlopen(requisicao, timeout=15) as resposta:
        if resposta.status != 200:
            raise RuntimeError("A imagem nao esta acessivel.")


def selecionar_celebracao(data_atual):
    """Retorna a celebracao cadastrada para a data informada."""

    return CELEBRACOES.get((data_atual.month, data_atual.day))


def testar_selecao():
    """Testa as datas cadastradas sem modificar o README."""

    datas_teste = [
        date(2026, 10, 31),
        date(2026, 11, 1),
        date(2026, 11, 2),
    ]

    for data_teste in datas_teste:
        celebracao = selecionar_celebracao(data_teste)

        if celebracao:
            print(f"{data_teste}: {celebracao['nome']}")
        else:
            print(f"{data_teste}: Nenhuma celebracao")


def atualizar_readme(caminho_readme=None, data_teste=None):
    """Atualiza somente a area reservada ao calendario."""

    # Usa a data real de Brasilia ou uma data de teste.
    if data_teste is None:
        data_atual = datetime.now(
            ZoneInfo("America/Sao_Paulo")
        ).date()
    else:
        data_atual = data_teste

    print(f"Data utilizada: {data_atual}")

    celebracao = selecionar_celebracao(data_atual)

    # Define o README principal ou um arquivo de teste.
    if caminho_readme is None:
        caminho_readme = Path(__file__).with_name("README.md")
    else:
        caminho_readme = Path(caminho_readme)

    if not caminho_readme.is_file():
        raise FileNotFoundError("README.md nao encontrado.")

    conteudo = caminho_readme.read_text(encoding="utf-8")

    # Confere se os dois marcadores existem uma unica vez.
    if conteudo.count(INICIO) != 1 or conteudo.count(FIM) != 1:
        raise ValueError(
            "Os marcadores do calendario estao ausentes ou duplicados."
        )

    posicao_inicio = conteudo.index(INICIO)
    posicao_fim = conteudo.index(FIM)

    # Impede a atualizacao se os marcadores estiverem invertidos.
    if posicao_inicio >= posicao_fim:
        raise ValueError("A ordem dos marcadores esta incorreta.")

    bloco = ""

    if celebracao:
        url_imagem = f"{REPOSITORIO}/{celebracao['imagem']}"

    # Se a imagem nao estiver acessivel, interrompe antes de escrever.
        verificar_imagem(url_imagem)

        bloco = (
            f"\n\n## 🎉 Especial de {celebracao['nome']}\n\n"
            "<div align=\"center\">\n\n"
            f'<img src="{url_imagem}" '
            f'alt="Banner de {celebracao["nome"]}" width="100%">\n\n'
            "</div>\n\n"
       )

    # Preserva todo o conteudo fora da area automatica.
    novo_conteudo = (
        conteudo[:posicao_inicio + len(INICIO)]
        + bloco
        + conteudo[posicao_fim:]
    )

    if novo_conteudo != conteudo:
        caminho_readme.write_text(
            novo_conteudo,
            encoding="utf-8"
        )
        print("README atualizado com sucesso!")
    else:
        print("O README ja esta atualizado.")

    if celebracao:
        print(f"Banner selecionado: {celebracao['nome']}")
    else:
        print("Nenhuma celebracao cadastrada para hoje.")


if __name__ == "__main__":
    atualizar_readme()