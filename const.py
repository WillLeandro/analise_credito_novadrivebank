consulta_sql = '''
                select 
                    c.profissao
                    ,c.tempoprofissao 
                    ,c.renda 
                    ,c.tiporesidencia 
                    ,c.escolaridade 
                    ,c.score 
                    ,extract( year from age(c.datanascimento ) ) as idade
                    ,c.dependentes
                    ,c.estadocivil
                    ,pf.nomecomercial as produto
                    ,valorsolicitado
                    ,valortotalbem
                    ,case when count(p.status) filter (where p.status = 'Vencido') > 0 then 'Ruim' else 'Bom' end as classe	
                from
                clientes c
                join pedidocredito pc on c.clienteid = pc.clienteid 
                join produtosfinanciados pf on pf.produtoid = pc.produtoid
                left join parcelascredito p on p.solicitacaoid = pc.solicitacaoid 
                where pc.status = 'Aprovado'
                group by c.clienteid, pf.nomecomercial, pc.valorsolicitado, pc.valortotalbem;

'''