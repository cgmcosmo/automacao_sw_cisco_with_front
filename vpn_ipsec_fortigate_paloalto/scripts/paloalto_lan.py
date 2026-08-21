from panos.network import EthernetInterface, Zone, VirtualRouter
import config_vpn


def configurar_lan(firewall):
    """
    Configura a interface LAN (ethernet1/1) do Palo Alto:
    - Define o IP da interface (gateway da rede local do Palo Alto)
    - Cria a zona LAN-ZONE e associa a interface
    - Associa a interface ao virtual router "default", preservando as
      interfaces já existentes (ethernet1/2, ethernet1/3, tunnel.1)
    """
    resultados = {}

    # Extrai o IP do gateway a partir da rede local (ex: 10.20.20.0/24 -> 10.20.20.1)
    rede, prefixo = config_vpn.PALOALTO_LOCAL_NETWORK.split("/")
    octetos = rede.split(".")
    octetos[-1] = "1"
    ip_gateway = ".".join(octetos)

    try:
        interface = EthernetInterface(
            name="ethernet1/1",
            mode="layer3",
            ip=[f"{ip_gateway}/{prefixo}"],
        )
        firewall.add(interface)
        interface.create()
        resultados["interface_lan"] = "OK"
    except Exception as erro:
        resultados["interface_lan"] = f"ERRO: {erro}"

    try:
        zona = Zone(
            name="LAN-ZONE",
            mode="layer3",
            interface=["ethernet1/1"],
        )
        firewall.add(zona)
        zona.create()
        resultados["zona_lan"] = "OK"
    except Exception as erro:
        resultados["zona_lan"] = f"ERRO: {erro}"

    try:
        vr = VirtualRouter(name="default")
        firewall.add(vr)
        vr.refresh()

        interfaces_atuais = list(vr.interface) if vr.interface else []
        if "ethernet1/1" not in interfaces_atuais:
            interfaces_atuais.append("ethernet1/1")
            vr.interface = interfaces_atuais
            vr.apply()
        resultados["virtual_router"] = "OK"
    except Exception as erro:
        resultados["virtual_router"] = f"ERRO: {erro}"

    return resultados