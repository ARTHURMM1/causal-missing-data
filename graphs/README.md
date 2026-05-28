
<h1 style="font-family: Arial, sans-serif; color: #333;">
    DAGs e Verificação de Missing Data
</h1>

<p style="font-family: Arial, sans-serif; line-height: 1.5;">
    Esta seção contém os DAGs causais e scripts utilizados para validar os mecanismos de missing data implementados nos DGPs do projeto.
</p>

<ul style="font-family: Arial, sans-serif; line-height: 1.5;">
    <li>MCAR</li>
    <li>MAR</li>
    <li>MNAR</li>
</ul>

<hr/>

<h2 style="font-family: Arial, sans-serif; color: #333;">
    Estrutura
</h2>

<pre style="background: #f0f0f0; padding: 10px; font-family: monospace;">
figure generator/
│
├── figure generator/
│   └── figure_DAG_gen.py
│
├── testes/
│   └── verify_dsep.py
│
├── images/
│   ├── mar_graph.png
│   └── ...
│
├── mar_graph.py
├── mnar_self_graph.py
├── proxy_mnar_graph.py
│
└── mar_graph.png
</pre>

<hr/>

<h2 style="font-family: Arial, sans-serif; color: #333;">
    MAR
</h2>

<p style="font-family: Arial, sans-serif; line-height: 1.5;">
    No cenário MAR, o mecanismo de missing depende apenas das variáveis observadas C.
</p>

<p style="font-family: Arial, sans-serif; font-weight: bold;">
    W indep RW | C
</p>

<p style="font-family: Arial, sans-serif; line-height: 1.5;">
    Após controlar C, o indicador de missing RW não contém mais informação sobre W.
</p>

<img src="images/mar_graph.png"
    alt="DAG MAR"
    style="max-width: 500px; margin-top: 15px;"
/>

<hr>

<h2 style="font-family: Arial, sans-serif; color: #333;">
    Self-MNAR
</h2>

<p style="font-family: Arial, sans-serif; line-height: 1.5;">
    No cenário self-MNAR, o missing depende diretamente da própria variável ausente.
</p>

<p style="font-family: Arial, sans-serif; font-weight: bold;">
    W NOT indep RW | C
</p>

<hr>

<h2 style="font-family: Arial, sans-serif; color: #333;">
    Proxy-MNAR
</h2>

<p style="font-family: Arial, sans-serif; line-height: 1.5;">
    No cenário proxy-MNAR, o missing depende de uma variável latente U.
</p>

<hr>

<h2 style="font-family: Arial, sans-serif; color: #333;">
    Verificação de d-separation
</h2>

<p style="font-family: Arial, sans-serif; line-height: 1.5;">
    O arquivo <code>verify_dsep.py</code> realiza verificações programáticas de independência condicional.
</p>

<table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
    <tr>
        <th style="border: 1px solid #999; padding: 8px;">
            Cenário
        </th>
        <th style="border: 1px solid #999; padding: 8px;">
            W indep RW | C
        </th>
    </tr>
    <tr>
        <td style="border: 1px solid #999; padding: 8px; text-align: center;">
            MAR
        </td>
        <td style="border: 1px solid #999; padding: 8px; text-align: center;">
            True
        </td>
    </tr>
    <tr>
        <td style="border: 1px solid #999; padding: 8px; text-align: center;">
            MNAR
        </td>
        <td style="border: 1px solid #999; padding: 8px; text-align: center;">
            False
        </td>
    </tr>

</table>

<hr>

<h2 style="font-family: Arial, sans-serif; color: #333;">
    Validação Empírica
</h2>

<p style="font-family: Arial, sans-serif; line-height: 1.5;">
    Os mecanismos também foram avaliados empiricamente utilizando regressões do tipo:
</p>

<pre style="background: #f0f0f0; padding: 10px; font-family: monospace;">
W1 ~ RW1 + C
</pre>

<table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
    <tr>
        <th style="border: 1px solid #999; padding: 8px;">
            Cenário
        </th>
        <th style="border: 1px solid #999; padding: 8px;">
            RW significativo após controlar C?
        </th>
    </tr>
    <tr>
        <td style="border: 1px solid #999; padding: 8px; text-align: center;">
            MAR
        </td>
        <td style="border: 1px solid #999; padding: 8px; text-align: center;">
            Não
        </td>
    </tr>
    <tr>
        <td style="border: 1px solid #999; padding: 8px; text-align: center;">
            MNAR
        </td>
        <td style="border: 1px solid #999; padding: 8px; text-align: center;">
            TODO
        </td>
    </tr>

</table>
