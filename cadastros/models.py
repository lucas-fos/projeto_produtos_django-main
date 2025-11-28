from django.db import models              # FRAMEWORK ORM


# USUARIO -> nome, email, idade
class Usuario(models.Model):
    nome = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    idade = models.IntegerField()
    
    def __str__(self):
        return self.nome
    
# PRODUTO -> nome, preco, estoque, criado
class Produto(models.Model):
    nome = models.CharField(max_length=50)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    estoque = models.IntegerField()
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='produtos'
    )
    
    def __str__(self):
        return self.nome
