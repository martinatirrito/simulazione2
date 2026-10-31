from database.DB_connect import DBConnect
from model.Arco import Arco
from model.album import Album


class DAO():
    @staticmethod
    def getAllGenre():

        conn = DBConnect.get_connection()
        if conn is None:
            print("Errore di connessione al database")
            return []
        cursor = conn.cursor(dictionary=True)

        result = []

        query = """select distinct g.Name as genere 
                    from genre g
                    order by g.Name asc"""

        cursor.execute(query, )

        for row in cursor:
            result.append(row["genere"])

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllYears():

        conn = DBConnect.get_connection()
        if conn is None:
            print("Errore di connessione al database")
            return []
        cursor = conn.cursor(dictionary=True)

        result = []

        query = """select distinct YEAR(i.InvoiceDate ) as anno
                    from Invoice i 
                    order by anno asc"""

        cursor.execute(query, )

        for row in cursor:
            result.append(row["anno"])

        cursor.close()
        conn.close()
        return result

    """
    I vertici sono gli album con almeno una traccia del genere G. Il valore di un album è la somma di InvoiceLine.
    Quantity delle sue tracce del genere G vendute nell’anno Y. Tieni solo gli album con valore ≥ S.
    C’è un arco tra due album se almeno un cliente, nell’anno Y, ha comprato tracce del genere G di entrambi. 
    L’arco va dal valore maggiore al minore, e a parità di valore si mettono entrambi gli archi. 
    Peso = numero di clienti distinti in comune.
    """
    @staticmethod
    def getAllNodes(genere, anno, soglia):

        conn = DBConnect.get_connection()
        if conn is None:
            print("Errore di connessione al database")
            return []
        cursor = conn.cursor(dictionary=True)

        result = []

        query = """select distinct a.AlbumId, a.Title, a.ArtistId, sum(il.Quantity) as valore
                    from Album a, track t, genre g, Invoice i, InvoiceLine il 
                    where a.AlbumId = t.AlbumId and t.GenreId = g.GenreId and t.TrackId = il.TrackId and il.InvoiceId = i.InvoiceId 
                    and g.Name = %s
                    and year(i.InvoiceDate) = %s
                    group by a.AlbumId 
                    having valore >= %s
                    order by a.Title asc"""

        cursor.execute(query, (genere, anno, soglia))

        for row in cursor:
            result.append(Album(**row))

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllEdges(idMapA, genere, anno, soglia):

        conn = DBConnect.get_connection()
        if conn is None:
            print("Errore di connessione al database")
            return []
        cursor = conn.cursor(dictionary=True)

        result = []
#qui non c'è bisogno che metto and a.id IN (QUERY CON HAVING) perchè l'having lo ho già nella sottoquery della somma, se non avessi avuto
        #l'orientamento dato dalla somma l'avrei dovuto mettere altrimenti having non spuntava da nessuna parte

        query = """select a1.AlbumId as a1, a2.AlbumId as a2, count(distinct a1.CustomerId) as peso
                    from (select distinct a.AlbumId, c.CustomerId 
                            from Album a, track t, genre g, Invoice i, InvoiceLine il, Customer c 
                            where a.AlbumId = t.AlbumId and t.GenreId = g.GenreId and t.TrackId = il.TrackId and il.InvoiceId = i.InvoiceId and i.CustomerId = c.CustomerId 
                            and g.Name = %s
                            and year(i.InvoiceDate) = %s) a1, (select distinct a.AlbumId, c.CustomerId 
                                                                        from Album a, track t, genre g, Invoice i, InvoiceLine il, Customer c 
                                                                        where a.AlbumId = t.AlbumId and t.GenreId = g.GenreId and t.TrackId = il.TrackId and il.InvoiceId = i.InvoiceId and i.CustomerId = c.CustomerId 
                                                                        and g.Name = %s
                                                                        and year(i.InvoiceDate) = %s)a2, 
                            (select distinct a.AlbumId , sum(il.Quantity) as somma
                                from Album a, track t, genre g, Invoice i, InvoiceLine il 
                                where a.AlbumId = t.AlbumId and t.GenreId = g.GenreId and t.TrackId = il.TrackId and il.InvoiceId = i.InvoiceId 
                                and g.Name = %s
                                and year(i.InvoiceDate) = %s
                                group by a.AlbumId 
                                having somma >= %s)	s1, (select distinct a.AlbumId , sum(il.Quantity) as somma
                                                        from Album a, track t, genre g, Invoice i, InvoiceLine il 
                                                        where a.AlbumId = t.AlbumId and t.GenreId = g.GenreId and t.TrackId = il.TrackId and il.InvoiceId = i.InvoiceId 
                                                        and g.Name = %s
                                                        and year(i.InvoiceDate) = %s
                                                        group by a.AlbumId 
                                                        having somma >= %s)	s2																		
                    where a1.CustomerId = a2.CustomerId 
                    and a1.AlbumId != a2.AlbumId 
                    and a1.AlbumId = s1.AlbumId and a2.AlbumId = s2.AlbumId 
                    and s1.somma >= s2.somma
                    group by a1.AlbumId , a2.AlbumId 
                    order by peso desc"""

        cursor.execute(query, (genere, anno, genere, anno, genere, anno, soglia,  genere, anno, soglia,   ))

        for row in cursor:
            result.append(Arco(idMapA[row["a1"]], idMapA[row["a2"]], row["peso"]))

        cursor.close()
        conn.close()
        return result