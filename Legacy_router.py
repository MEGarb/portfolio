#!/usr/bin/python
from mininet.examples.linuxrouter import LinuxRouter
from mininet.net import Mininet
from mininet.node import Controller
from mininet.node import Host
from mininet.node import OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info


def my_network():
    net = Mininet(topo=None, build=False, ipBase='0.0.0.0')

    info('*** Adding controller\n')
    c0 = net.addController(name='c0', controller=Controller, protocol='tcp', port=6633)

    info('*** Add switches\n')
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)

    info('*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.3.1/24', defaultRoute='via 10.0.3.254')
    h2 = net.addHost('h2', cls=Host, ip='10.0.5.1/24', defaultRoute='via 10.0.5.254')

    info('*** Add routers\n')
    r3 = net.addHost('r3', cls=LinuxRouter, ip='10.0.3.254/24')
    r3.cmd('sysctl net.ipv4.ip_forward=1')
    r4 = net.addHost('r4', cls=LinuxRouter, ip='192.168.1.254/30')
    r4.cmd('sysctl net.ipv4.ip_forward=1')
    r5 = net.addHost('r5', cls=LinuxRouter, ip='192.168.2.253/30')
    r5.cmd('sysctl net.ipv4.ip_forward=1')

    info('*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(r3, s1)
    net.addLink(r3, r4, intfName1='r3-eth1', params1={'ip': '192.168.1.253/30'})
    net.addLink(r4, r5, intfName1='r4-eth1', params1={'ip': '192.168.2.254/30'})
    net.addLink(r5, s2, intfName1='r5-eth1', params1={'ip': '10.0.5.254/24'})

    info('*** Starting network\n')
    net.build()
    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting switches\n')
    net.get('s2').start([c0])
    net.get('s1').start([c0])

    info('*** Entering Routes In Routing Tables:\n')
    # Add routing for reaching networks that aren't directly connected
    info(net['r3'].cmd('ip route add 10.0.5.0/24 via 192.168.1.254 dev r3-eth1'))
    info(net['r3'].cmd('ip route add 192.168.2.252/30 via 192.168.1.254 dev r3-eth1'))
    info(net['r4'].cmd('ip route add 10.0.3.0/24 via 192.168.1.253 dev r4-eth0'))
    info(net['r4'].cmd('ip route add 10.0.5.0/24 via 192.168.2.253 dev r4-eth1'))
    info(net['r5'].cmd('ip route add 10.0.3.0/24 via 192.168.2.254 dev r5-eth0'))
    info(net['r5'].cmd('ip route add 192.168.1.252/30 via 192.168.2.254 dev r5-eth0'))

    info('*** Post configure switches and hosts\n')

    # info('*** Routing Table on Router:\n')
    # print(net['r3'].cmd('route'))
    # print(net['r4'].cmd('route'))
    # print(net['r5'].cmd('route'))

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    my_network()
