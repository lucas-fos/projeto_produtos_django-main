from django.db import models

class Artista(models.Model):
    nome = models.CharField(max_length=100)
    nacionalidade = models.CharField(max_length=50)
    biografia = models.TextField(blank=True)
    data_nascimento = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nome


class Obra(models.Model):
    TIPOS_ARTE = [
        ('Pintura', 'Pintura'),
        ('Escultura', 'Escultura'),
        ('Fotografia', 'Fotografia'),
        ('Digital', 'Arte Digital'),
    ]

    titulo = models.CharField(max_length=100)
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE)
    descricao = models.TextField()
    ano = models.IntegerField()
    tipo = models.CharField(max_length=20, choices=TIPOS_ARTE)
    imagem = models.ImageField(upload_to='obras/', blank=True, null=True)

    def __str__(self):
        return self.titulo


class Exposicao(models.Model):
    nome = models.CharField(max_length=100)
    local = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    obras = models.ManyToManyField(Obra)

    def __str__(self):
        return self.nome
