<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>DAGs e Missing Data</title>

<style>
    body {
        font-family: Arial, sans-serif;
        margin: 40px;
        line-height: 1.5;
    }

    h1, h2 {
        color: #333;
    }

    pre {
        background: #f0f0f0;
        padding: 10px;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        margin-top: 10px;
    }

    table, th, td {
        border: 1px solid #999;
    }

    th, td {
        padding: 8px;
        text-align: center;
    }

    img {
        max-width: 500px;
        margin-top: 15px;
    }
</style>
</head>

<body>

<h1>DAGs e Verificação de Missing Data</h1>

<p>
Esta seção contém os DAGs causais e scripts utilizados para validar os mecanismos de missing data implementados nos DGPs do projeto.
</p>

<ul>
    <li>MCAR</li>
    <li>MAR</li>
    <li>MNAR</li>
</ul>

<hr>

<h2>Estrutura</h2>

<pre>
figure generator/
│
├── figure generator/
    └── figure_DAG_gen.py
├── testes/
    └── verify_dsep.py
├── images/
│   ├── mar_graph.png
    └──... TODO
├── mar_graph.py
├── mnar_self_graph.py
├── proxy_mnar_graph.py
│
└── mar_graph.png
</pre>

<hr>

<h2>MAR</h2>

<p>
No cenário MAR, o mecanismo de missing depende apenas das variáveis observadas C.
</p>

<p>
W indep RW | C
</p>

<p>
Após controlar C, o indicador de missing RW não contém mais informação sobre W.
</p>

<img src="images/mar_graph.png" alt="DAG MAR">

<hr>

<h2>Self-MNAR</h2>

<p>
No cenário self-MNAR, o missing depende diretamente da própria variável ausente.
</p>

<p>
W NOT indep RW | C
</p>

<hr>

<h2>Proxy-MNAR</h2>

<p>
No cenário proxy-MNAR, o missing depende de uma variável latente U.
</p>

<hr>

<h2>Verificação de d-separation</h2>

<p>
O arquivo <code>verify_dsep.py</code> realiza verificações programáticas de independência condicional.
</p>

<table>
    <tr>
        <th>Cenário</th>
        <th>W indep RW | C</th>
    </tr>

    <tr>
        <td>MAR</td>
        <td>True</td>
    </tr>

    <tr>
        <td>MNAR</td>
        <td>False</td>
    </tr>
</table>

<hr>

<h2>Validação Empírica</h2>

<p>
Os mecanismos também foram avaliados empiricamente utilizando regressões do tipo:
</p>

<pre>
W1 ~ RW1 + C
</pre>

<table>
    <tr>
        <th>Cenário</th>
        <th>RW significativo após controlar C?</th>
    </tr>

    <tr>
        <td>MAR</td>
        <td>Não</td>
    </tr>

    <tr>
        <td>MNAR</td>
        <td>TODO</td>
    </tr>
</table>

</body>
</html>