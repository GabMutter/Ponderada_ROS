import rclpy
from rclpy.node import Node
from turtlesim.srv import TeleportAbsolute, SetPen
import math
import os

from contorno_dog.imagem_processing import extrair_caminho

class TurtleDrawNode(Node):
    def __init__(self, caminho):
        super().__init__('turtle_draw_node')
        self.caminho = caminho
        self.teleport_client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        
        while not self.teleport_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Aguardando serviço de teletransporte...')
        while not self.pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Aguardando serviço da caneta...')

    
    def set_pen(self, off_value):
        req = SetPen.Request()
        req.r, req.g, req.b = 255, 255, 255
        req.width = 1
        req.off = off_value
        future = self.pen_client.call_async(req)
        # O código congela aqui até o Turtlesim confirmar que a caneta mudou
        rclpy.spin_until_future_complete(self, future)

    def teleport(self, x, y):
        req = TeleportAbsolute.Request()
        req.x = float(x)
        req.y = float(y)
        req.theta = 0.0
        future = self.teleport_client.call_async(req)
        # O código congela aqui até o Turtlesim confirmar que se moveu
        rclpy.spin_until_future_complete(self, future)

    
    def desenhar(self):
        self.get_logger().info('Iniciando desenho (com ordem estrita garantida)...')
        
        self.set_pen(1) # Começa com a caneta levantada
        x_anterior, y_anterior = None, None
        
        for x, y in self.caminho:
            if x_anterior is not None:
                distancia = math.sqrt((x - x_anterior)**2 + (y - y_anterior)**2)
                
                # Se pular longe, levanta a caneta
                if distancia > 0.2: 
                    self.set_pen(1)
            
            # Teleporta pro local
            self.teleport(x, y)
            
            # Abaixa para marcar o contorno
            self.set_pen(0)
            
            x_anterior = x
            y_anterior = y
            
        self.get_logger().info('Desenho finalizado!')

def main(args=None):
    rclpy.init(args=args)
    
    try:
        caminho_da_imagem = 'src/contorno_dog/contorno_dog/dog.jpg'
        if not os.path.exists(caminho_da_imagem):
            caminho_da_imagem = 'dog.jpg' 
            
        caminho_final = extrair_caminho(caminho_da_imagem)
        
        node = TurtleDrawNode(caminho_final)
        
        node.desenhar()
        
        node.destroy_node()
        
    except Exception as e:
        print(f"Erro ao executar a pipeline: {e}")
    finally:
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()